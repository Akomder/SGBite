"""Repositories: all database queries live here. Layer: DATA ACCESS."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from ..domain.models import (ACTIVE_FOR_LOAD, CONFIRMED, PLACED, Brand, Hub, HubMenuItem, MenuItem,
                             Notification, Order, OrderItem, PREPARING, READY, OUT_FOR_DELIVERY,
                             User, Voucher, VoucherRedemption)


class _Repo:
    def __init__(self, session):
        self.session = session

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def flush(self):
        self.session.flush()


class UserRepository(_Repo):
    def get(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def by_username(self, username: str) -> User | None:
        return self.session.scalar(select(User).where(User.username == username))

    def add(self, user: User) -> User:
        self.session.add(user)
        return user

    def count(self) -> int:
        return self.session.scalar(select(func.count(User.id))) or 0


class HubRepository(_Repo):
    def all(self) -> list[Hub]:
        return list(self.session.scalars(select(Hub).order_by(Hub.id)))

    def get(self, hub_id: int) -> Hub | None:
        return self.session.get(Hub, hub_id)

    def add(self, hub: Hub) -> Hub:
        self.session.add(hub)
        return hub

    def active_orders(self, hub_id: int) -> int:
        """Orders that count towards hub load (A-04)."""
        return self.session.scalar(
            select(func.count(Order.id)).where(Order.hub_id == hub_id, Order.status.in_(ACTIVE_FOR_LOAD))) or 0


class MenuRepository(_Repo):
    def brands(self) -> list[Brand]:
        return list(self.session.scalars(select(Brand).order_by(Brand.name)))

    def add(self, obj):
        self.session.add(obj)
        return obj

    def available_items(self, hub_id: int) -> list[MenuItem]:
        stmt = (select(MenuItem).join(HubMenuItem, HubMenuItem.menu_item_id == MenuItem.id)
                .where(HubMenuItem.hub_id == hub_id, HubMenuItem.available.is_(True))
                .options(selectinload(MenuItem.brand)).order_by(MenuItem.brand_id, MenuItem.id))
        return list(self.session.scalars(stmt))


class VoucherRepository(_Repo):
    def get(self, voucher_id: int) -> Voucher | None:
        return self.session.get(Voucher, voucher_id)

    def by_code(self, code: str) -> Voucher | None:
        return self.session.scalar(select(Voucher).where(Voucher.code == code))

    def add(self, voucher: Voucher) -> Voucher:
        self.session.add(voucher)
        return voucher

    def all(self) -> list[Voucher]:
        return list(self.session.scalars(select(Voucher).order_by(Voucher.id.desc())))

    def search(self, text: str = "") -> list[Voucher]:
        stmt = select(Voucher).order_by(Voucher.id.desc())
        if text:
            like = f"%{text.upper()}%"
            stmt = stmt.where(func.upper(Voucher.code).like(like) | func.upper(Voucher.description).like(like))
        return list(self.session.scalars(stmt))

    def used_by(self, voucher_id: int, customer_id: int) -> bool:
        n = self.session.scalar(select(func.count(VoucherRedemption.id)).where(
            VoucherRedemption.voucher_id == voucher_id, VoucherRedemption.customer_id == customer_id))
        return bool(n)

    def add_redemption(self, redemption: VoucherRedemption) -> None:
        self.session.add(redemption)


class OrderRepository(_Repo):
    def add(self, order: Order) -> Order:
        self.session.add(order)
        return order

    def get(self, order_id: int) -> Order | None:
        return self.session.get(Order, order_id)

    def for_customer(self, customer_id: int) -> list[Order]:
        stmt = select(Order).where(Order.customer_id == customer_id).order_by(Order.id.desc())
        return list(self.session.scalars(stmt))

    def incoming(self, hub_id: int) -> list[Order]:
        """New orders for a hub, oldest first (UC2)."""
        stmt = select(Order).where(Order.hub_id == hub_id, Order.status == PLACED).order_by(Order.created_at, Order.id)
        return list(self.session.scalars(stmt))

    def in_progress(self, hub_id: int) -> list[Order]:
        stmt = (select(Order).where(Order.hub_id == hub_id,
                                    Order.status.in_([CONFIRMED, PREPARING, READY, OUT_FOR_DELIVERY]))
                .order_by(Order.created_at, Order.id))
        return list(self.session.scalars(stmt))

    def for_reports(self, start: datetime, end: datetime, hub_id: int | None = None) -> list[Order]:
        stmt = (select(Order).where(Order.created_at >= start, Order.created_at <= end)
                .options(selectinload(Order.items).selectinload(OrderItem.menu_item).selectinload(MenuItem.brand),
                         selectinload(Order.hub))
                .order_by(Order.created_at))
        if hub_id:
            stmt = stmt.where(Order.hub_id == hub_id)
        return list(self.session.scalars(stmt))


class NotificationRepository(_Repo):
    def add(self, user_id: int, message: str, order_id: int | None = None) -> None:
        self.session.add(Notification(user_id=user_id, order_id=order_id, message=message))

    def for_user(self, user_id: int, limit: int = 10) -> list[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id).order_by(Notification.id.desc()).limit(limit)
        return list(self.session.scalars(stmt))
