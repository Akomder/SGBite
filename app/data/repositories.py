"""Query and persistence operations kept out of controllers."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.data.models import Order, Voucher


class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, order_id: int) -> Order | None:
        return self.session.get(Order, order_id)

    def list_recent(self, limit: int = 50) -> list[Order]:
        return list(self.session.scalars(select(Order).order_by(Order.created_at.desc()).limit(limit)))

    def add(self, order: Order) -> Order:
        self.session.add(order)
        self.session.flush()
        return order


class VoucherRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, voucher_id: int) -> Voucher | None:
        return self.session.get(Voucher, voucher_id)

    def list_all(self) -> list[Voucher]:
        return list(self.session.scalars(select(Voucher).order_by(Voucher.code)))

    def count_orders(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(Order)) or 0)
