from datetime import timedelta

import pytest

from app.domain.errors import NotFound, ValidationError
from app.domain.models import now
from app.domain.vouchers import VoucherService


def form(**kw):
    today = now().date()
    base = {"code": "summer25", "description": "Summer", "discount_type": "percent", "value": "25",
            "valid_from": str(today), "valid_to": str(today + timedelta(days=30)), "min_order": "50000",
            "usage_limit": "", "once_per_customer": "1"}
    base.update(kw)
    return base


def test_create_read_update_deactivate(session):
    svc = VoucherService(session)
    v = svc.create(form())
    assert v.code == "SUMMER25" and v.usage_limit is None
    assert any(r[0].id == v.id for r in svc.list("summer"))
    svc.update(v.id, form(value="30", description="Changed"))
    assert (v.value, v.description) == (30, "Changed") and v.code == "SUMMER25"
    svc.deactivate(v.id)
    assert svc.list("SUMMER25", "Deactivated")[0][0].id == v.id


@pytest.mark.parametrize("changes", [
    {"code": "a!"}, {"code": "WELCOME10"}, {"discount_type": "other"}, {"value": "0"}, {"value": "150"},
    {"value": "abc"}, {"valid_to": "2000-01-01"}, {"valid_from": "nope"}, {"min_order": "-5"}, {"usage_limit": "0"},
])
def test_invalid_voucher_input_is_rejected(session, changes):
    with pytest.raises(ValidationError):
        VoucherService(session).create(form(**changes))


def test_expired_voucher_cannot_be_updated(session):
    svc = VoucherService(session)
    expired = svc.list("OLD5")[0][0]
    with pytest.raises(ValidationError):
        svc.update(expired.id, form())


def test_usage_limit_cannot_drop_below_used_count(session, make_order):
    make_order(qty=2, voucher="WELCOME10")  # used_count = 1
    svc = VoucherService(session)
    v = svc.list("WELCOME10")[0][0]
    svc.update(v.id, form(code="x", usage_limit="1"))  # equal to used count is fine
    with pytest.raises(ValidationError):
        svc.update(v.id, form(usage_limit="0"))


def test_deactivated_voucher_cannot_be_used_but_history_stays(session, make_order):
    from app.domain.errors import VoucherError
    order = make_order(qty=2, voucher="WELCOME10")
    svc = VoucherService(session)
    svc.deactivate(order.voucher_id)
    assert order.voucher_discount == 13_000  # past order keeps its voucher
    with pytest.raises(VoucherError):
        make_order(customer="tourist", qty=2, voucher="WELCOME10", payment="cash")


def test_unknown_voucher(session):
    with pytest.raises(NotFound):
        VoucherService(session).get(9999)
