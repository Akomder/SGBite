"""Sample data for demos and tests. Layer: DATA ACCESS."""
from __future__ import annotations

import random
from datetime import timedelta

from ..domain import pricing
from ..domain.models import (ADMIN, CUSTOMER, DELIVERED, FAILED, KITCHEN, LOCAL, MANAGER, PAID,
                             PENDING_CASH, COLLECTED, TOURIST, Brand, Hub, HubMenuItem, MenuItem,
                             Order, OrderItem, User, Voucher, now)
from .repositories import UserRepository

DEV_PASSWORD = "password"  # development only: change before any real use

MENU = [
    ("SaigonBite Pho", "Phở bò tái", "Rare beef pho", 65_000),
    ("SaigonBite Pho", "Phở gà", "Chicken pho", 55_000),
    ("SaigonBite Rice", "Cơm tấm sườn", "Broken rice with pork chop", 60_000),
    ("SaigonBite Rice", "Cơm gà xối mỡ", "Crispy chicken rice", 58_000),
    ("SaigonBite Banh Mi", "Bánh mì thịt nướng", "Grilled pork banh mi", 35_000),
    ("SaigonBite Banh Mi", "Bánh mì trứng", "Egg banh mi", 25_000),
]


def seed(db, password_method: str = "pbkdf2:sha256", demo_orders: bool = True) -> bool:
    """Create sample data if the database is empty. Returns True if data was added."""
    s = db.session
    users = UserRepository(s)
    if users.count():
        return False
    at = now()

    hubs = [Hub(name="Hub District 1", address="12 Nguyen Hue, District 1", capacity=10),
            Hub(name="Hub Thu Duc", address="45 Vo Van Ngan, Thu Duc", capacity=8)]
    s.add_all(hubs)
    brands = {n: Brand(name=n) for n in dict.fromkeys(m[0] for m in MENU)}
    s.add_all(brands.values())
    s.flush()
    items = []
    for brand, vi, en, price in MENU:
        item = MenuItem(brand_id=brands[brand].id, name_vi=vi, name_en=en, price=price)
        s.add(item)
        items.append(item)
    s.flush()
    for hub in hubs:
        for item in items:
            # Hub Thu Duc has run out of egg banh mi (shows availability per hub)
            available = not (hub.name == "Hub Thu Duc" and item.name_en == "Egg banh mi")
            s.add(HubMenuItem(hub_id=hub.id, menu_item_id=item.id, available=available))

    def make_user(username, name, role, **kw):
        u = User(username=username, full_name=name, role=role, **kw)
        u.set_password(DEV_PASSWORD, method=password_method)
        s.add(u)
        return u

    an = make_user("an", "Nguyen Van An", CUSTOMER, customer_type=LOCAL, phone="0901234567")
    tourist = make_user("tourist", "Emma Jones", CUSTOMER, customer_type=TOURIST, email="emma@example.com")
    make_user("kitchen1", "Kitchen staff Hub D1", KITCHEN, hub_id=hubs[0].id)
    make_user("kitchen2", "Kitchen staff Hub Thu Duc", KITCHEN, hub_id=hubs[1].id)
    make_user("admin", "Admin", ADMIN)
    make_user("manager", "Manager", MANAGER)

    s.add_all([
        Voucher(code="WELCOME10", description="10% off the items", discount_type="percent", value=10,
                valid_from=at - timedelta(days=30), valid_to=at + timedelta(days=60), min_order=100_000,
                usage_limit=100),
        Voucher(code="SAVE20K", description="20,000 VND off", discount_type="fixed", value=20_000,
                valid_from=at - timedelta(days=30), valid_to=at + timedelta(days=60), min_order=150_000),
        Voucher(code="OLD5", description="Expired example", discount_type="percent", value=5,
                valid_from=at - timedelta(days=90), valid_to=at - timedelta(days=30)),
    ])
    s.flush()
    if demo_orders:
        _demo_orders(s, [an, tourist], hubs, items, at)
    s.commit()
    return True


def _demo_orders(s, customers, hubs, items, at, count: int = 30) -> None:
    """Delivered and failed orders over the last 10 days so the reports have data."""
    rng = random.Random(5)
    for _ in range(count):
        hub = rng.choice(hubs)
        customer = rng.choice(customers)
        chosen = rng.sample(items, rng.randint(1, 3))
        qtys = {i.id: rng.randint(1, 2) for i in chosen}
        subtotal = sum(i.price * qtys[i.id] for i in chosen)
        distance = round(rng.uniform(0.5, 6.5), 1)
        price = pricing.calculate(subtotal, distance, False, "normal")
        created = (at - timedelta(days=rng.randint(1, 10))).replace(
            hour=rng.choice([11, 12, 12, 13, 18, 19, 19, 20]), minute=rng.randint(0, 59), second=0, microsecond=0)
        failed = rng.random() < 0.1
        cash = rng.random() < 0.4
        order = Order(customer_id=customer.id, hub_id=hub.id, status=FAILED if failed else DELIVERED,
                      delivery_address="Demo address", distance_km=distance, items_subtotal=subtotal,
                      delivery_fee=price.delivery_fee, total=price.total,
                      payment_method="cash" if cash else ("card" if customer.customer_type == TOURIST else "ewallet"),
                      payment_status=PENDING_CASH if (cash and failed) else (COLLECTED if cash else PAID),
                      created_at=created, confirmed_at=created + timedelta(minutes=3))
        if not failed:
            order.delivered_at = created + timedelta(minutes=rng.randint(25, 62))
        order.items = [OrderItem(menu_item_id=i.id, quantity=qtys[i.id], unit_price=i.price) for i in chosen]
        s.add(order)
        s.flush()
        order.number = f"SB{created:%y%m%d}-{order.id:05d}"
