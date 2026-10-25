"""UC2 Confirm or reject an incoming order (owner 523V0017). Layer: DOMAIN."""
from __future__ import annotations

from ..data.repositories import HubRepository, NotificationRepository, OrderRepository
from .errors import NotAllowed, NotFound
from .models import KITCHEN, Order, User, now
from .ordering import HubStatus


class KitchenService:
    def __init__(self, session):
        self.hubs = HubRepository(session)
        self.orders = OrderRepository(session)
        self.notifications = NotificationRepository(session)

    def _staff_hub(self, staff: User):
        if staff.role != KITCHEN or staff.hub_id is None:
            raise NotAllowed("Only kitchen staff assigned to a hub can do this.")
        return self.hubs.get(staff.hub_id)

    def hub_status(self, staff: User) -> HubStatus:
        hub = self._staff_hub(staff)
        active = self.hubs.active_orders(hub.id)
        return HubStatus(hub, active, hub.load_ratio(active), hub.state(active))

    def incoming_orders(self, staff: User) -> list[Order]:
        """New orders of the staff member's hub, oldest first."""
        return self.orders.incoming(self._staff_hub(staff).id)

    def in_progress_orders(self, staff: User) -> list[Order]:
        return self.orders.in_progress(self._staff_hub(staff).id)

    def _own_order(self, staff: User, order_id: int) -> Order:
        hub = self._staff_hub(staff)
        order = self.orders.get(order_id)
        if order is None:
            raise NotFound("Order not found.")
        if order.hub_id != hub.id:  # A-16: staff see only their own hub's orders
            raise NotAllowed("This order belongs to another hub.")
        return order

    def confirm(self, staff: User, order_id: int, at=None) -> Order:
        at = at or now()
        order = self._own_order(staff, order_id)
        order.confirm(at)
        self.notifications.add(order.customer_id, f"Order {order.number} was confirmed by the kitchen.", order.id)
        self.orders.commit()
        return order

    def reject(self, staff: User, order_id: int, reason: str, at=None) -> Order:
        at = at or now()
        order = self._own_order(staff, order_id)
        order.reject(reason, at)  # reason required; online payment refunded (A-07, A-09)
        refund = " Your online payment is refunded in full." if order.payment_status == "Refunded" else ""
        self.notifications.add(order.customer_id,
                               f"Order {order.number} was rejected: {order.reject_reason}.{refund}", order.id)
        self.orders.commit()
        return order

    def advance(self, staff: User, order_id: int, new_status: str, at=None) -> Order:
        """Supporting step (outside our four use cases): move an order along kitchen and delivery steps."""
        at = at or now()
        order = self._own_order(staff, order_id)
        order.advance(new_status, at)
        self.notifications.add(order.customer_id, f"Order {order.number} is now {order.status}.", order.id)
        self.orders.commit()
        return order
