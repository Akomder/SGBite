"""UC3 Manage vouchers (owner 523K0076). Layer: DOMAIN.

Create, read (list and search), update and deactivate. A voucher is never
deleted, so past orders keep their history (requirement: deactivate or archive).
"""
from __future__ import annotations

import re
from datetime import date, datetime, time

from ..data.repositories import VoucherRepository
from .errors import NotFound, ValidationError
from .models import Voucher, now

CODE_RE = re.compile(r"^[A-Z0-9]{3,20}$")
STATES = ("Active", "Scheduled", "Used up", "Expired", "Deactivated")


def _int(raw, label, minimum=0, required=True):
    raw = (raw if raw is not None else "").strip() if isinstance(raw, str) else raw
    if raw in ("", None):
        if required:
            raise ValidationError(f"{label} is required.")
        return None
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise ValidationError(f"{label} must be a whole number.")
    if value < minimum:
        raise ValidationError(f"{label} must be at least {minimum}.")
    return value


def _day(raw, label, end_of_day=False) -> datetime:
    try:
        d = date.fromisoformat((raw or "").strip())
    except ValueError:
        raise ValidationError(f"{label} must be a date (YYYY-MM-DD).")
    return datetime.combine(d, time(23, 59, 59) if end_of_day else time(0, 0, 0))


class VoucherService:
    def __init__(self, session):
        self.vouchers = VoucherRepository(session)

    # ---- read -------------------------------------------------------------------
    def list(self, text: str = "", state: str = "", at=None) -> list[tuple[Voucher, str]]:
        at = at or now()
        rows = [(v, v.state(at)) for v in self.vouchers.search((text or "").strip())]
        if state:
            rows = [r for r in rows if r[1] == state]
        return rows

    def get(self, voucher_id: int) -> Voucher:
        voucher = self.vouchers.get(voucher_id)
        if voucher is None:
            raise NotFound("Voucher not found.")
        return voucher

    # ---- validation ---------------------------------------------------------------
    def _parse(self, data: dict) -> dict:
        discount_type = (data.get("discount_type") or "").strip()
        if discount_type not in ("percent", "fixed"):
            raise ValidationError("Choose a discount type: percent or fixed amount.")
        value = _int(data.get("value"), "Discount value", 1)
        if discount_type == "percent" and value > 100:
            raise ValidationError("A percentage discount cannot be more than 100.")
        valid_from = _day(data.get("valid_from"), "Valid from")
        valid_to = _day(data.get("valid_to"), "Valid to", end_of_day=True)
        if valid_to <= valid_from:
            raise ValidationError("Valid to must be after valid from.")
        return {
            "description": (data.get("description") or "").strip()[:200],
            "discount_type": discount_type, "value": value,
            "valid_from": valid_from, "valid_to": valid_to,
            "min_order": _int(data.get("min_order") or "0", "Minimum order", 0),
            "usage_limit": _int(data.get("usage_limit"), "Usage limit", 1, required=False),
            "once_per_customer": bool(data.get("once_per_customer")),
        }

    # ---- create ---------------------------------------------------------------------
    def create(self, data: dict) -> Voucher:
        code = (data.get("code") or "").strip().upper()
        if not CODE_RE.match(code):
            raise ValidationError("Code must be 3 to 20 letters or digits.")
        if self.vouchers.by_code(code):
            raise ValidationError(f"Voucher code {code} already exists.")
        voucher = Voucher(code=code, **self._parse(data))
        self.vouchers.add(voucher)
        self.vouchers.commit()
        return voucher

    # ---- update -----------------------------------------------------------------------
    def update(self, voucher_id: int, data: dict, at=None) -> Voucher:
        at = at or now()
        voucher = self.get(voucher_id)
        if voucher.state(at) == "Expired":
            raise ValidationError("An expired voucher cannot be changed.")
        fields = self._parse(data)
        if fields["usage_limit"] is not None and fields["usage_limit"] < voucher.used_count:
            raise ValidationError("Usage limit cannot be lower than the times the voucher was already used.")
        for key, value in fields.items():
            setattr(voucher, key, value)  # the code itself never changes
        self.vouchers.commit()
        return voucher

    # ---- deactivate -----------------------------------------------------------------------
    def deactivate(self, voucher_id: int) -> Voucher:
        voucher = self.get(voucher_id)
        voucher.active = False
        self.vouchers.commit()
        return voucher
