"""UC1 Place an order (owner 523K0076). Layer: DOMAIN."""
from __future__ import annotations

from dataclasses import dataclass, field

from ..data.repositories import (HubRepository, MenuRepository, NotificationRepository, OrderRepository,
                                 VoucherRepository)
from . import pricing
from .errors import HubFullError, NotAllowed, NotFound, ValidationError, VoucherError
from .models import (CUSTOMER, LOCAL, PAID, PENDING_CASH, TOURIST, Hub, MenuItem, Order, OrderItem, User,
                     Voucher, VoucherRedemption, now)

# A-08: payment options depend on the customer type
ALLOWED_PAYMENTS = {LOCAL: ("ewallet", "bank_qr", "cash"), TOURIST: ("card", "cash")}
MAX_QTY_PER_ITEM = 20


@dataclass
class HubStatus:
    hub: Hub
    active_orders: int
    ratio: float
    state: str


@dataclass
class Quote:
    hub: Hub
    hub_state: str
    lines: list  # (MenuItem, quantity, line_total)
    breakdown: pricing.PriceBreakdown
    voucher: Voucher | None
    payment_method: str
    distance_km: float
    address: str
    suggestions: list = field(default_factory=list)  # quieter hubs when this hub is busy


class OrderingService:
    def __init__(self, session):
        self.hubs = HubRepository(session)
        self.menu = MenuRepository(session)
        self.vouchers = VoucherRepository(session)
        self.orders = OrderRepository(session)
        self.notifications = NotificationRepository(session)

    # ---- hubs and menu -----------------------------------------------------
    def hub_status(self, hub: Hub) -> HubStatus:
        active = self.hubs.active_orders(hub.id)
        return HubStatus(hub, active, hub.load_ratio(active), hub.state(active))

    def hub_overview(self) -> list[HubStatus]:
        return [self.hub_status(h) for h in self.hubs.all()]

    def get_hub(self, hub_id: int) -> Hub:
        hub = self.hubs.get(hub_id)
        if hub is None:
            raise NotFound("Hub not found.")
        return hub

    def menu_for(self, hub_id: int) -> list[MenuItem]:
        return self.menu.available_items(hub_id)

    def allowed_payments(self, customer: User) -> tuple:
        return ALLOWED_PAYMENTS.get(customer.customer_type or LOCAL, ALLOWED_PAYMENTS[LOCAL])

    def _suggestions(self, current: Hub) -> list[HubStatus]:
        others = [s for s in self.hub_overview() if s.hub.id != current.id and s.state in ("quiet", "normal")]
        return sorted(others, key=lambda s: s.ratio)

    # ---- price quote (the customer sees the full price before confirming) ---
    def quote(self, customer: User, hub_id: int, quantities: dict[int, int], distance_km, address: str,
              voucher_code: str, payment_method: str, at=None) -> Quote:
        at = at or now()
        if customer.role != CUSTOMER:
            raise NotAllowed("Only customers can place orders.")
        hub = self.get_hub(hub_id)
        status = self.hub_status(hub)
        if status.state == "full":  # A-04: stops accepting new orders at 100% load
            raise HubFullError("This hub is not accepting new orders right now.", self._suggestions(hub))

        address = (address or "").strip()
        if not address:
            raise ValidationError("Enter a delivery address.")
        try:
            distance = float(distance_km)
        except (TypeError, ValueError):
            raise ValidationError("Enter the distance from the hub in km.")

        wanted = {i: q for i, q in quantities.items() if q and q > 0}
        if not wanted:
            raise ValidationError("Choose at least one item.")
        available = {m.id: m for m in self.menu_for(hub_id)}
        lines = []
        for item_id, qty in wanted.items():
            item = available.get(item_id)
            if item is None:
                raise ValidationError("An item you chose is not available at this hub.")
            if qty > MAX_QTY_PER_ITEM:
                raise ValidationError(f"You can order at most {MAX_QTY_PER_ITEM} of one item.")
            lines.append((item, qty, item.price * qty))
        subtotal = sum(line[2] for line in lines)

        if payment_method not in self.allowed_payments(customer):
            raise ValidationError("This payment method is not available for your account.")

        voucher, discount = None, 0
        code = (voucher_code or "").strip().upper()
        if code:
            voucher = self.vouchers.by_code(code)
            if voucher is None:
                raise VoucherError("Voucher code not found.")
            voucher.check_applicable(subtotal, at, self.vouchers.used_by(voucher.id, customer.id))
            discount = voucher.discount_for(subtotal)

        breakdown = pricing.calculate(subtotal, distance, hub.rain_mode, status.state, discount)
        suggestions = self._suggestions(hub) if status.state == "busy" else []
        return Quote(hub, status.state, lines, breakdown, voucher, payment_method, distance, address, suggestions)

    # ---- place the order ------------------------------------------------------
    def place(self, customer: User, hub_id: int, quantities: dict[int, int], distance_km, address: str,
              voucher_code: str, payment_method: str, at=None) -> Order:
        at = at or now()
        q = self.quote(customer, hub_id, quantities, distance_km, address, voucher_code, payment_method, at)
        b = q.breakdown
        online = q.payment_method != "cash"  # A-08: online payment is taken at placement (simulated gateway)
        order = Order(customer_id=customer.id, hub_id=q.hub.id, delivery_address=q.address,
                      distance_km=q.distance_km, items_subtotal=b.items_subtotal, delivery_fee=b.delivery_fee,
                      rain_surcharge=b.rain_surcharge, quiet_discount=b.quiet_discount,
                      voucher_id=q.voucher.id if q.voucher else None, voucher_discount=b.voucher_discount,
                      total=b.total, payment_method=q.payment_method,
                      payment_status=PAID if online else PENDING_CASH, created_at=at)
        order.items = [OrderItem(menu_item_id=item.id, quantity=qty, unit_price=item.price)
                       for item, qty, _ in q.lines]
        self.orders.add(order)
        self.orders.flush()
        order.number = f"SB{at:%y%m%d}-{order.id:05d}"
        if q.voucher:
            q.voucher.used_count += 1
            self.vouchers.add_redemption(VoucherRedemption(voucher_id=q.voucher.id, customer_id=customer.id,
                                                           order_id=order.id))
        self.notifications.add(customer.id, f"Order {order.number} was placed at {q.hub.name}.", order.id)
        self.orders.commit()
        return order

    # ---- customer views ---------------------------------------------------------
    def my_orders(self, customer: User) -> list[Order]:
        return self.orders.for_customer(customer.id)

    def get_order(self, customer: User, order_id: int) -> Order:
        order = self.orders.get(order_id)
        if order is None:
            raise NotFound("Order not found.")
        if order.customer_id != customer.id:
            raise NotAllowed("This is not your order.")
        return order

    def cancel(self, customer: User, order_id: int, at=None) -> Order:
        at = at or now()
        order = self.get_order(customer, order_id)
        order.cancel(at)  # A-06: only while Placed or Confirmed
        self.notifications.add(customer.id, f"Order {order.number} was cancelled.", order.id)
        self.orders.commit()
        return order

    def notifications_for(self, customer: User):
        return self.notifications.for_user(customer.id)
