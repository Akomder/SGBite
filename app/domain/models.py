"""Persistent domain classes with their business behaviour.

Layer: DOMAIN. These classes are mapped to tables by SQLAlchemy (section 4.3.1
of the report). Business rules (state machine, voucher rules, hub load) live
here, not in controllers.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from .errors import InvalidTransition, ValidationError, VoucherError


def now() -> datetime:
    """Naive UTC time (works the same on SQLite and PostgreSQL)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


# ---- constants -------------------------------------------------------------
CUSTOMER, KITCHEN, ADMIN, MANAGER = "customer", "kitchen", "admin", "manager"
LOCAL, TOURIST = "local", "tourist"

PLACED, CONFIRMED, REJECTED, CANCELLED = "Placed", "Confirmed", "Rejected", "Cancelled"
PREPARING, READY, OUT_FOR_DELIVERY = "Preparing", "Ready", "Out for delivery"
DELIVERED, FAILED = "Delivered", "Failed"

# Assumption A-14: the order state machine
TRANSITIONS = {
    PLACED: {CONFIRMED, REJECTED, CANCELLED},
    CONFIRMED: {PREPARING, CANCELLED},
    PREPARING: {READY},
    READY: {OUT_FOR_DELIVERY},
    OUT_FOR_DELIVERY: {DELIVERED, FAILED},
}
ACTIVE_FOR_LOAD = (CONFIRMED, PREPARING)  # Assumption A-04

PAID, PENDING_CASH, COLLECTED = "Paid", "Pending (cash)", "Collected"
REFUNDED, NOT_CHARGED = "Refunded", "Not charged"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(40), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(80))
    role: Mapped[str] = mapped_column(String(20))
    customer_type: Mapped[str | None] = mapped_column(String(10), nullable=True)  # local / tourist
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    hub_id: Mapped[int | None] = mapped_column(ForeignKey("hubs.id"), nullable=True)  # kitchen staff

    def set_password(self, raw: str, method: str = "pbkdf2:sha256") -> None:
        self.password_hash = generate_password_hash(raw, method=method)

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password_hash, raw)


class Hub(Base):
    __tablename__ = "hubs"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    address: Mapped[str] = mapped_column(String(200))
    capacity: Mapped[int] = mapped_column(Integer)
    rain_mode: Mapped[bool] = mapped_column(Boolean, default=False)

    QUIET_UP_TO = 0.40  # A-05
    BUSY_FROM = 0.80    # A-04
    FULL_AT = 1.00      # A-04

    def load_ratio(self, active_orders: int) -> float:
        return active_orders / self.capacity if self.capacity > 0 else 1.0

    def state(self, active_orders: int) -> str:
        ratio = self.load_ratio(active_orders)
        if ratio >= self.FULL_AT:
            return "full"
        if ratio >= self.BUSY_FROM:
            return "busy"
        if ratio <= self.QUIET_UP_TO:
            return "quiet"
        return "normal"


class Brand(Base):
    __tablename__ = "brands"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)


class MenuItem(Base):
    __tablename__ = "menu_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"))
    name_vi: Mapped[str] = mapped_column(String(120))
    name_en: Mapped[str] = mapped_column(String(120))
    price: Mapped[int] = mapped_column(Integer)  # VND, whole number (A-02)
    brand: Mapped[Brand] = relationship()

    def name(self, lang: str) -> str:
        return self.name_vi if lang == "vi" else self.name_en


class HubMenuItem(Base):
    """Which menu items a hub can serve right now."""
    __tablename__ = "hub_menu_items"
    hub_id: Mapped[int] = mapped_column(ForeignKey("hubs.id"), primary_key=True)
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"), primary_key=True)
    available: Mapped[bool] = mapped_column(Boolean, default=True)


class Voucher(Base):
    __tablename__ = "vouchers"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    description: Mapped[str] = mapped_column(String(200), default="")
    discount_type: Mapped[str] = mapped_column(String(10))  # percent / fixed (A-10)
    value: Mapped[int] = mapped_column(Integer)
    valid_from: Mapped[datetime] = mapped_column(DateTime)
    valid_to: Mapped[datetime] = mapped_column(DateTime)
    min_order: Mapped[int] = mapped_column(Integer, default=0)
    usage_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    once_per_customer: Mapped[bool] = mapped_column(Boolean, default=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    def state(self, at: datetime) -> str:
        """Voucher lifecycle: Scheduled, Active, Used up, Expired, Deactivated."""
        if not self.active:
            return "Deactivated"
        if at > self.valid_to:
            return "Expired"
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return "Used up"
        if at < self.valid_from:
            return "Scheduled"
        return "Active"

    def check_applicable(self, items_subtotal: int, at: datetime, already_used: bool) -> None:
        state = self.state(at)
        if state != "Active":
            raise VoucherError(f"Voucher {self.code} cannot be used: it is {state.lower()}.")
        if items_subtotal < self.min_order:
            raise VoucherError(f"Voucher {self.code} needs a minimum order of {self.min_order:,} VND.")
        if self.once_per_customer and already_used:
            raise VoucherError(f"Voucher {self.code} was already used by this customer.")

    def discount_for(self, items_subtotal: int) -> int:
        """Discount applies to the items subtotal only, never to the delivery fee (A-10)."""
        if self.discount_type == "percent":
            amount = items_subtotal * self.value // 100
        else:
            amount = self.value
        return max(0, min(amount, items_subtotal))


class VoucherRedemption(Base):
    __tablename__ = "voucher_redemptions"
    __table_args__ = (UniqueConstraint("order_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    voucher_id: Mapped[int] = mapped_column(ForeignKey("vouchers.id"))
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    hub_id: Mapped[int] = mapped_column(ForeignKey("hubs.id"))
    status: Mapped[str] = mapped_column(String(20), default=PLACED)
    delivery_address: Mapped[str] = mapped_column(String(250))
    distance_km: Mapped[float] = mapped_column(Float)
    items_subtotal: Mapped[int] = mapped_column(Integer)
    delivery_fee: Mapped[int] = mapped_column(Integer)
    rain_surcharge: Mapped[int] = mapped_column(Integer, default=0)
    quiet_discount: Mapped[int] = mapped_column(Integer, default=0)
    voucher_id: Mapped[int | None] = mapped_column(ForeignKey("vouchers.id"), nullable=True)
    voucher_discount: Mapped[int] = mapped_column(Integer, default=0)
    total: Mapped[int] = mapped_column(Integer)
    payment_method: Mapped[str] = mapped_column(String(20))
    payment_status: Mapped[str] = mapped_column(String(20))
    reject_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    items: Mapped[list["OrderItem"]] = relationship(cascade="all, delete-orphan", order_by="OrderItem.id")
    customer: Mapped[User] = relationship(foreign_keys=[customer_id])
    hub: Mapped[Hub] = relationship()
    voucher: Mapped[Voucher | None] = relationship()

    # ---- state machine (UC1 creates Placed; UC2 confirms or rejects) -------
    def _move(self, new: str) -> None:
        if new not in TRANSITIONS.get(self.status, set()):
            raise InvalidTransition(f"An order that is {self.status} cannot become {new}.")
        self.status = new

    def confirm(self, at: datetime) -> None:
        self._move(CONFIRMED)
        self.confirmed_at = at

    def reject(self, reason: str, at: datetime) -> None:
        reason = (reason or "").strip()
        if len(reason) < 3:
            raise ValidationError("A reason is required to reject an order.")
        self._move(REJECTED)
        self.reject_reason = reason
        self._release_payment()

    def cancel(self, at: datetime) -> None:
        if self.status not in (PLACED, CONFIRMED):  # A-06
            raise InvalidTransition("An order can only be cancelled while it is Placed or Confirmed.")
        self._move(CANCELLED)
        self._release_payment()

    def advance(self, new: str, at: datetime) -> None:
        """Supporting step outside our four use cases (kitchen and shipper progress)."""
        if new in (CONFIRMED, REJECTED, CANCELLED):
            raise InvalidTransition(f"Use the confirm, reject or cancel action to make an order {new}.")
        self._move(new)
        if new == DELIVERED:
            self.delivered_at = at
            if self.payment_status == PENDING_CASH:
                self.payment_status = COLLECTED

    def _release_payment(self) -> None:
        """A-07: online payments are refunded in full; cash orders were never charged."""
        self.payment_status = REFUNDED if self.payment_status == PAID else NOT_CHARGED

    def next_steps(self) -> list[str]:
        return sorted(s for s in TRANSITIONS.get(self.status, set()) if s not in (CONFIRMED, REJECTED, CANCELLED))


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[int] = mapped_column(Integer)  # price at order time
    menu_item: Mapped[MenuItem] = relationship()

    @property
    def line_total(self) -> int:
        return self.quantity * self.unit_price


class Notification(Base):
    """Simulated notification (the real SMS or push service is out of scope, A-18)."""
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"), nullable=True)
    message: Mapped[str] = mapped_column(String(250))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
