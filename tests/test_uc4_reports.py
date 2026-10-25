from datetime import date, datetime, timedelta

import pytest

from app.domain.errors import ValidationError
from app.domain.models import now
from app.domain.reports import ReportFilter, ReportService


def deliver(order, minutes, at):
    order.confirmed_at = at
    order.delivered_at = at + timedelta(minutes=minutes)
    order.status = "Delivered"


@pytest.fixture
def delivered(session, make_order):
    at = now()
    a = make_order(qty=2, distance=3.0)                      # hub 0: 130,000 + 25,000 - 5,000 = 150,000
    b = make_order(hub=1, item="Chicken pho", qty=1, distance=1.0)  # hub 1: 55,000 + 15,000 - 5,000 = 65,000
    deliver(a, 30, at)
    deliver(b, 60, at)
    make_order(qty=1)  # still Placed: must not count as sales
    session.commit()
    return a, b


def flt(**kw):
    today = date.today()
    return ReportFilter(today - timedelta(days=1), today + timedelta(days=1), **kw)


def table(rep, title):
    return next(rows for t, _h, rows in rep.tables if t == title)


def test_sales_totals_only_delivered_orders(session, delivered):
    rep = ReportService(session).sales(flt())
    summary = dict(rep.summary)
    assert summary["Revenue (VND)"] == "215,000" and summary["Delivered orders"] == 2
    assert summary["Average order value (VND)"] == "107,500"
    assert dict((r[0], r[2]) for r in table(rep, "By hub")) == {"Hub District 1": "150,000", "Hub Thu Duc": "65,000"}


def test_sales_filter_by_hub_and_brand(session, delivered, hubs):
    svc = ReportService(session)
    assert dict(svc.sales(flt(hub_id=hubs[1].id)).summary)["Revenue (VND)"] == "65,000"
    pho_brand = delivered[0].items[0].menu_item.brand_id
    brand = dict(svc.sales(flt(brand_id=pho_brand)).summary)
    assert brand["Revenue (VND)"] == "185,000"  # item amounts only: 130,000 + 55,000


def test_delivery_performance(session, delivered):
    summary = dict(ReportService(session).delivery(flt()).summary)
    assert summary["Delivered orders"] == 2
    assert summary["Average delivery time (minutes, Confirmed to Delivered)"] == "45.0"
    assert summary["Late deliveries (over 45 minutes)"].startswith("1 (50%)")
    assert summary["Failed deliveries"].startswith("0")


def test_failed_deliveries_are_counted(session, make_order):
    o = make_order()
    o.status = "Failed"
    session.commit()
    assert dict(ReportService(session).delivery(flt()).summary)["Failed deliveries"].startswith("1 (100%)")


def test_workload_shows_peak_hour_against_capacity(session, make_order, hubs):
    at = now().replace(hour=12, minute=0, second=0, microsecond=0)
    for _ in range(3):
        make_order(at=at)
    rep = ReportService(session).workload(ReportFilter(at.date(), at.date()))
    row = table(rep, "Peak hour against capacity")[0]
    assert row[0] == "Hub District 1" and row[2] == "12:00" and row[3] == "3.0" and row[4] == "30%"


def test_filter_parsing_and_validation():
    f = ReportFilter.parse({"date_from": "2026-01-01", "date_to": "2026-01-31", "hub_id": "2"})
    assert (f.date_from, f.hub_id) == (date(2026, 1, 1), 2)
    with pytest.raises(ValidationError):
        ReportFilter.parse({"date_from": "2026-02-01", "date_to": "2026-01-01"})
    with pytest.raises(ValidationError):
        ReportFilter.parse({"date_from": "bad"})
    default = ReportFilter.parse({}, today=date(2026, 10, 30))
    assert (default.date_from, default.date_to) == (date(2026, 9, 30), date(2026, 10, 30))


def test_csv_rows_include_summary_and_tables(session, delivered):
    rows = ReportService(session).sales(flt()).csv_rows()
    flat = [c for r in rows for c in r]
    assert "Sales report" in flat and "By hub" in flat and "Hub Thu Duc" in flat
