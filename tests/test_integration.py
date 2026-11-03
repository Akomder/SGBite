"""Integration of the four use cases: one business scenario that crosses UC3, UC1, UC2 and UC4.

Scenario A: an admin creates a voucher (UC3); a tourist uses it to place an order (UC1); kitchen staff confirm
it (UC2) and it is delivered; the manager's reports (UC4) include it.
Scenario B: a second order is rejected by the kitchen (UC2): the customer is refunded and told why, and the
sales report does not count it.
"""
import re
from datetime import date, timedelta

from app.data.repositories import OrderRepository
from app.domain.models import Order


def _login(client, username):
    client.get("/logout")
    return client.post("/login", data={"username": username, "password": "password"}, follow_redirects=True)


def _order_form(items, **extra):
    data = {f"qty_{items['Rare beef pho'].id}": "2", "address": "Hotel Saigon, District 1", "distance_km": "3.0",
            "voucher": "INTEG10", "payment": "card"}
    data.update(extra)
    return data


def _last_order(session):
    orders = session.query(Order).order_by(Order.id.desc()).all()
    return orders[0]


def test_scenario_a_voucher_order_confirm_deliver_report(client, session, hubs, items):
    # UC3: admin creates a voucher
    _login(client, "admin")
    today = date.today()
    page = client.post("/admin/vouchers/new", data={
        "code": "INTEG10", "description": "Integration test", "discount_type": "percent", "value": "10",
        "valid_from": str(today - timedelta(days=1)), "valid_to": str(today + timedelta(days=30)),
        "min_order": "50000", "usage_limit": "", "once_per_customer": "1"}, follow_redirects=True)
    assert b"Voucher created" in page.data and b"INTEG10" in page.data

    # UC1: a tourist places an order with that voucher
    _login(client, "tourist")
    preview = client.post(f"/order/hub/{hubs[0].id}/preview", data=_order_form(items))
    assert b"137,000 VND" in preview.data  # 130,000 + 25,000 - 5,000 (quiet hub) - 13,000 (voucher)
    placed = client.post(f"/order/hub/{hubs[0].id}/place", data=_order_form(items), follow_redirects=True)
    assert b"Your order was placed" in placed.data
    order = _last_order(session)
    assert (order.status, order.total, order.voucher_discount, order.payment_status) == ("Placed", 137_000, 13_000, "Paid")
    assert order.voucher.used_count == 1

    # UC2: kitchen staff of that hub see it and confirm it
    _login(client, "kitchen1")
    assert order.number.encode() in client.get("/kitchen").data
    assert b"Order confirmed" in client.post(f"/kitchen/orders/{order.id}/confirm", follow_redirects=True).data
    session.refresh(order)
    assert order.status == "Confirmed"
    for step in ("Preparing", "Ready", "Out for delivery", "Delivered"):  # supporting steps outside the four use cases
        client.post(f"/kitchen/orders/{order.id}/advance", data={"status": step}, follow_redirects=True)
    session.refresh(order)
    assert order.status == "Delivered" and order.delivered_at is not None

    # UC4: the manager's reports include the order
    _login(client, "manager")
    sales = client.get("/reports/sales").get_data(as_text=True)
    assert "137,000" in sales
    delivery = client.get("/reports/delivery").get_data(as_text=True)
    assert "Delivered orders" in delivery and "Hub District 1" in delivery
    csv = client.get("/reports/sales?format=csv").get_data(as_text=True)
    assert "Revenue (VND)" in csv and "137,000" in csv

    # the customer sees the final state and the notifications
    _login(client, "tourist")
    detail = client.get(f"/orders/{order.id}").get_data(as_text=True)
    assert "Delivered" in detail and "was confirmed by the kitchen" in detail


def test_scenario_b_reject_refund_and_report(client, session, hubs, items):
    _login(client, "tourist")
    data = _order_form(items, voucher="")
    client.post(f"/order/hub/{hubs[0].id}/place", data=data, follow_redirects=True)
    order = _last_order(session)
    assert order.payment_status == "Paid"

    _login(client, "kitchen1")
    rejected = client.post(f"/kitchen/orders/{order.id}/reject", data={"reason": "Beef pho is sold out"}, follow_redirects=True)
    assert b"Order rejected" in rejected.data
    session.refresh(order)
    assert (order.status, order.payment_status) == ("Rejected", "Refunded")

    _login(client, "tourist")
    detail = client.get(f"/orders/{order.id}").get_data(as_text=True)
    assert "Beef pho is sold out" in detail and "refunded in full" in detail

    _login(client, "manager")
    sales = client.get("/reports/sales").get_data(as_text=True)
    assert "Delivered orders" in sales and "<b>0</b>" in sales  # a rejected order is not a sale
