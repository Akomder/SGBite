import pytest

from app.domain.errors import InvalidTransition, NotAllowed, ValidationError
from app.domain.kitchen import KitchenService


def test_incoming_orders_are_for_own_hub_oldest_first(session, make_order, users):
    first, second = make_order(), make_order()
    other_hub = make_order(hub=1, item="Chicken pho")
    ids = [o.id for o in KitchenService(session).incoming_orders(users["kitchen1"])]
    assert ids == [first.id, second.id] and other_hub.id not in ids


def test_confirm_changes_state_and_notifies_customer(session, make_order, users):
    o = make_order()
    KitchenService(session).confirm(users["kitchen1"], o.id)
    assert o.status == "Confirmed" and o.confirmed_at is not None
    from app.data.repositories import NotificationRepository
    assert any("confirmed" in n.message for n in NotificationRepository(session).for_user(users["an"].id))


def test_reject_requires_reason_and_refunds(session, make_order, users):
    o = make_order()
    svc = KitchenService(session)
    with pytest.raises(ValidationError):
        svc.reject(users["kitchen1"], o.id, "")
    svc.reject(users["kitchen1"], o.id, "Item out of stock")
    assert (o.status, o.reject_reason, o.payment_status) == ("Rejected", "Item out of stock", "Refunded")


def test_cannot_confirm_twice_or_reject_after_confirm(session, make_order, users):
    o = make_order()
    svc = KitchenService(session)
    svc.confirm(users["kitchen1"], o.id)
    with pytest.raises(InvalidTransition):
        svc.confirm(users["kitchen1"], o.id)
    with pytest.raises(InvalidTransition):
        svc.reject(users["kitchen1"], o.id, "too late")


def test_staff_cannot_touch_another_hubs_orders(session, make_order, users):
    o = make_order(hub=1, item="Chicken pho")
    with pytest.raises(NotAllowed):
        KitchenService(session).confirm(users["kitchen1"], o.id)


def test_only_kitchen_staff_can_use_the_service(session, users):
    with pytest.raises(NotAllowed):
        KitchenService(session).incoming_orders(users["an"])


def test_hub_load_counts_confirmed_orders(session, make_order, users):
    svc = KitchenService(session)
    for _ in range(3):
        svc.confirm(users["kitchen1"], make_order().id)
    status = svc.hub_status(users["kitchen1"])
    assert (status.active_orders, status.state) == (3, "quiet")  # 3/10 = 30%
