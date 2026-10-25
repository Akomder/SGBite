from datetime import timedelta

import pytest

from app.domain.errors import InvalidTransition, ValidationError, VoucherError
from app.domain.models import Hub, Order, Voucher, now


def voucher(**kw):
    base = dict(code="T1", discount_type="percent", value=10, valid_from=now() - timedelta(days=1),
                valid_to=now() + timedelta(days=1), min_order=0, usage_limit=None, used_count=0,
                once_per_customer=True, active=True)
    base.update(kw)
    return Voucher(**base)


@pytest.mark.parametrize("active,expected", [(0, "quiet"), (4, "quiet"), (5, "normal"), (7, "normal"), (8, "busy"), (9, "busy"), (10, "full"), (12, "full")])
def test_hub_state_thresholds(active, expected):
    assert Hub(capacity=10).state(active) == expected


def test_voucher_states():
    at = now()
    assert voucher().state(at) == "Active"
    assert voucher(active=False).state(at) == "Deactivated"
    assert voucher(valid_to=at - timedelta(seconds=1)).state(at) == "Expired"
    assert voucher(valid_from=at + timedelta(days=1), valid_to=at + timedelta(days=2)).state(at) == "Scheduled"
    assert voucher(usage_limit=3, used_count=3).state(at) == "Used up"


def test_voucher_discount_is_percent_or_fixed_and_never_more_than_items():
    assert voucher(value=10).discount_for(200_000) == 20_000
    assert voucher(discount_type="fixed", value=30_000).discount_for(200_000) == 30_000
    assert voucher(discount_type="fixed", value=30_000).discount_for(20_000) == 20_000


def test_voucher_rules():
    at = now()
    with pytest.raises(VoucherError):
        voucher(min_order=100_000).check_applicable(50_000, at, False)
    with pytest.raises(VoucherError):
        voucher().check_applicable(50_000, at, True)
    voucher(once_per_customer=False).check_applicable(50_000, at, True)  # allowed


def order(status="Placed", paid=True):
    return Order(status=status, payment_status="Paid" if paid else "Pending (cash)", payment_method="card")


def test_order_state_machine_happy_path():
    o = order()
    at = now()
    o.confirm(at)
    for step in ("Preparing", "Ready", "Out for delivery", "Delivered"):
        o.advance(step, at)
    assert o.status == "Delivered" and o.delivered_at == at


def test_reject_needs_reason_and_refunds_online_payment():
    with pytest.raises(ValidationError):
        order().reject("  ", now())
    o = order()
    o.reject("item out of stock", now())
    assert (o.status, o.payment_status) == ("Rejected", "Refunded")
    cash = order(paid=False)
    cash.reject("item out of stock", now())
    assert cash.payment_status == "Not charged"


def test_invalid_transitions_are_blocked():
    o = order()
    with pytest.raises(InvalidTransition):
        o.advance("Preparing", now())  # must be confirmed first
    o.confirm(now())
    with pytest.raises(InvalidTransition):
        o.reject("late", now())  # only Placed orders can be rejected


def test_cancel_only_while_placed_or_confirmed():
    o = order("Preparing")
    with pytest.raises(InvalidTransition):
        o.cancel(now())
    p = order()
    p.cancel(now())
    assert (p.status, p.payment_status) == ("Cancelled", "Refunded")
