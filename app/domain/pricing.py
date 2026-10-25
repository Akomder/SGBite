"""Price rules for UC1 (assumptions A-01 to A-05). Layer: DOMAIN."""
from __future__ import annotations

from dataclasses import dataclass

from .errors import ValidationError

MAX_DISTANCE_KM = 7.0                                     # A-01
FEE_BANDS = ((2.0, 15_000), (4.0, 25_000), (7.0, 35_000))  # A-02: (up to km, fee in VND)
RAIN_SURCHARGE = 10_000                                   # A-03
QUIET_DISCOUNT = 5_000                                    # A-05


@dataclass(frozen=True)
class PriceBreakdown:
    items_subtotal: int
    delivery_fee: int
    rain_surcharge: int
    quiet_discount: int
    voucher_discount: int
    total: int


def delivery_fee(distance_km: float) -> int:
    if distance_km <= 0:
        raise ValidationError("Distance must be greater than 0 km.")
    if distance_km > MAX_DISTANCE_KM:
        raise ValidationError(f"We deliver up to {MAX_DISTANCE_KM:g} km from the hub.")
    for limit, fee in FEE_BANDS:
        if distance_km <= limit:
            return fee
    raise ValidationError("Distance is outside the delivery area.")  # unreachable


def calculate(items_subtotal: int, distance_km: float, rain_mode: bool,
              hub_state: str, voucher_discount: int = 0) -> PriceBreakdown:
    fee = delivery_fee(distance_km)
    rain = RAIN_SURCHARGE if rain_mode else 0
    quiet = min(QUIET_DISCOUNT, fee) if hub_state == "quiet" else 0
    total = max(0, items_subtotal + fee + rain - quiet - voucher_discount)
    return PriceBreakdown(items_subtotal, fee, rain, quiet, voucher_discount, total)
