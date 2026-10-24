"""Order rules shared by UC1 (place) and UC2 (confirm/reject)."""
from decimal import Decimal, InvalidOperation

from app.data.models import Order, OrderItem, OrderStatus


def create_order(customer_name: str, delivery_address: str, items: list[dict[str, object]]) -> Order:
    if not customer_name.strip() or not delivery_address.strip():
        raise ValueError("Customer name and delivery address are required.")
    if not items:
        raise ValueError("An order must contain at least one item.")
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise ValueError("Order items must be a list of item objects.")
    order = Order(customer_name=customer_name.strip(), delivery_address=delivery_address.strip())
    for item in items:
        name = str(item.get("name", "")).strip()
        try:
            quantity = int(item.get("quantity", 0))
            price = Decimal(str(item.get("unit_price", "0")))
        except (ValueError, TypeError, InvalidOperation) as error:
            raise ValueError("Quantity and unit price must be valid numbers.") from error
        if not price.is_finite():
            raise ValueError("Unit price must be a finite number.")
        if not name or quantity < 1 or price < 0:
            raise ValueError("Each item needs a name, positive quantity, and non-negative price.")
        order.items.append(OrderItem(item_name=name, quantity=quantity, unit_price=price))
    order.total_amount = sum((i.unit_price * i.quantity for i in order.items), start=Decimal("0.00"))
    return order


def confirm_order(order: Order) -> None:
    if order.status != OrderStatus.PENDING.value:
        raise ValueError("Only pending orders can be confirmed or rejected.")
    order.status = OrderStatus.CONFIRMED.value
    order.rejection_reason = None


def reject_order(order: Order, reason: str) -> None:
    if order.status != OrderStatus.PENDING.value:
        raise ValueError("Only pending orders can be confirmed or rejected.")
    if not reason.strip():
        raise ValueError("A rejection reason is required.")
    order.status = OrderStatus.REJECTED.value
    order.rejection_reason = reason.strip()
