"""Voucher rules for UC3."""
from datetime import datetime, timezone
from decimal import Decimal

from app.data.models import Voucher


def validate_voucher(code: str, discount_percent: Decimal) -> None:
    if not code.strip():
        raise ValueError("Voucher code is required.")
    if discount_percent <= 0 or discount_percent > 100:
        raise ValueError("Discount must be greater than 0 and at most 100 percent.")


def is_voucher_usable(voucher: Voucher, now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    if not voucher.active:
        return False
    expiry = voucher.expires_at
    if expiry is None:
        return True
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    return expiry >= now
