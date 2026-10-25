import pytest

from app.domain import pricing
from app.domain.errors import ValidationError


@pytest.mark.parametrize("km,fee", [(0.5, 15_000), (2.0, 15_000), (2.1, 25_000), (4.0, 25_000), (4.1, 35_000), (7.0, 35_000)])
def test_delivery_fee_bands(km, fee):
    assert pricing.delivery_fee(km) == fee


@pytest.mark.parametrize("km", [0, -1, 7.1, 20])
def test_distance_outside_area_is_rejected(km):
    with pytest.raises(ValidationError):
        pricing.delivery_fee(km)


def test_total_adds_fee_and_rain_and_subtracts_discounts():
    b = pricing.calculate(100_000, 3.0, rain_mode=True, hub_state="quiet", voucher_discount=10_000)
    assert (b.delivery_fee, b.rain_surcharge, b.quiet_discount, b.voucher_discount) == (25_000, 10_000, 5_000, 10_000)
    assert b.total == 100_000 + 25_000 + 10_000 - 5_000 - 10_000


def test_quiet_discount_only_for_quiet_hubs():
    assert pricing.calculate(50_000, 1.0, False, "normal").quiet_discount == 0
    assert pricing.calculate(50_000, 1.0, False, "quiet").quiet_discount == 5_000
