import pytest

from app.domain.errors import HubFullError, NotAllowed, ValidationError, VoucherError
from app.domain.models import Order
from app.domain.ordering import OrderingService


def test_place_order_creates_placed_order_with_full_price(make_order):
    o = make_order(qty=2, distance=3.0)  # 2 x 65,000, hub is quiet (0/10)
    assert o.status == "Placed" and o.number.startswith("SB")
    assert (o.items_subtotal, o.delivery_fee, o.quiet_discount) == (130_000, 25_000, 5_000)
    assert o.total == 130_000 + 25_000 - 5_000
    assert o.payment_status == "Paid"  # online payment is taken at placement


def test_cash_order_is_pending_payment(make_order):
    assert make_order(payment="cash").payment_status == "Pending (cash)"


def test_voucher_applied_and_counted(make_order, session):
    o = make_order(qty=2, voucher="welcome10")  # 130,000 >= 100,000 minimum
    assert o.voucher_discount == 13_000
    assert o.voucher.used_count == 1


def test_one_use_per_customer(make_order):
    make_order(qty=2, voucher="WELCOME10")
    with pytest.raises(VoucherError):
        make_order(qty=2, voucher="WELCOME10")


def test_voucher_errors(make_order):
    with pytest.raises(VoucherError):
        make_order(qty=1, voucher="WELCOME10")  # below minimum order
    with pytest.raises(VoucherError):
        make_order(voucher="OLD5")  # expired
    with pytest.raises(VoucherError):
        make_order(voucher="NOPE")  # unknown


@pytest.mark.parametrize("distance", [0, 7.5, "abc"])
def test_distance_validation(make_order, distance):
    with pytest.raises(ValidationError):
        make_order(distance=distance)


def test_payment_options_depend_on_customer_type(make_order):
    with pytest.raises(ValidationError):
        make_order(customer="tourist", payment="ewallet")
    with pytest.raises(ValidationError):
        make_order(customer="an", payment="card")
    assert make_order(customer="tourist", payment="card").payment_method == "card"


def test_item_not_available_at_hub(session, users, hubs, items):
    egg = items["Egg banh mi"]  # unavailable at Hub Thu Duc
    with pytest.raises(ValidationError):
        OrderingService(session).place(users["an"], hubs[1].id, {egg.id: 1}, 2, "x", "", "cash")


def test_empty_order_and_missing_address(session, users, hubs, items):
    svc = OrderingService(session)
    with pytest.raises(ValidationError):
        svc.place(users["an"], hubs[0].id, {}, 2, "x", "", "cash")
    with pytest.raises(ValidationError):
        svc.place(users["an"], hubs[0].id, {items["Rare beef pho"].id: 1}, 2, "  ", "", "cash")


def test_only_customers_can_order(session, users, hubs, items):
    with pytest.raises(NotAllowed):
        OrderingService(session).place(users["admin"], hubs[0].id, {items["Rare beef pho"].id: 1}, 2, "x", "", "cash")


def _fill_hub(session, make_order, users, hubs, n):
    from app.domain.kitchen import KitchenService
    kitchen = KitchenService(session)
    for _ in range(n):
        o = make_order(payment="cash", voucher="")
        kitchen.confirm(users["kitchen1"], o.id)


def test_busy_hub_warns_and_suggests_quieter_hub(session, make_order, users, hubs, items):
    _fill_hub(session, make_order, users, hubs, 8)  # 8 / 10 = 80% -> busy
    q = OrderingService(session).quote(users["an"], hubs[0].id, {items["Rare beef pho"].id: 1}, 2, "x", "", "cash")
    assert q.hub_state == "busy" and [s.hub.id for s in q.suggestions] == [hubs[1].id]
    assert q.breakdown.quiet_discount == 0


def test_full_hub_stops_accepting_orders(session, make_order, users, hubs, items):
    _fill_hub(session, make_order, users, hubs, 10)
    with pytest.raises(HubFullError) as err:
        OrderingService(session).place(users["an"], hubs[0].id, {items["Rare beef pho"].id: 1}, 2, "x", "", "cash")
    assert err.value.suggestions


def test_customer_can_cancel_early_but_not_others_orders(session, make_order, users):
    o = make_order()
    svc = OrderingService(session)
    with pytest.raises(NotAllowed):
        svc.cancel(users["tourist"], o.id)
    svc.cancel(users["an"], o.id)
    assert session.get(Order, o.id).status == "Cancelled"
    assert session.get(Order, o.id).payment_status == "Refunded"
