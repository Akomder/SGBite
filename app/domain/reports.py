"""UC4 Produce management reports (owner 523V0017). Layer: DOMAIN.

Reports use only orders held in the system (A-12). Calculations happen in
Python so they work the same on SQLite and PostgreSQL.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

from ..data.repositories import HubRepository, MenuRepository, OrderRepository
from .errors import ValidationError
from .models import DELIVERED, FAILED, Order

LATE_AFTER_MINUTES = 45  # A-20


@dataclass
class ReportFilter:
    date_from: date
    date_to: date
    hub_id: int | None = None
    brand_id: int | None = None

    @classmethod
    def parse(cls, args, today: date | None = None) -> "ReportFilter":
        today = today or date.today()

        def day(key, default):
            raw = (args.get(key) or "").strip()
            if not raw:
                return default
            try:
                return date.fromisoformat(raw)
            except ValueError:
                raise ValidationError("Dates must look like YYYY-MM-DD.")

        def number(key):
            raw = (args.get(key) or "").strip()
            if not raw:
                return None
            try:
                return int(raw)
            except ValueError:
                raise ValidationError("Hub and brand must be numbers.")

        f = cls(day("date_from", today - timedelta(days=30)), day("date_to", today), number("hub_id"), number("brand_id"))
        if f.date_from > f.date_to:
            raise ValidationError("The start date must not be after the end date.")
        return f

    @property
    def start(self) -> datetime:
        return datetime.combine(self.date_from, time.min)

    @property
    def end(self) -> datetime:
        return datetime.combine(self.date_to, time.max)


@dataclass
class Report:
    title: str
    summary: list = field(default_factory=list)  # (label, value)
    tables: list = field(default_factory=list)   # (title, headers, rows)

    def csv_rows(self) -> list[list]:
        out = [[self.title], []]
        out += [[k, v] for k, v in self.summary]
        for title, headers, rows in self.tables:
            out += [[], [title], headers] + [list(r) for r in rows]
        return out


class ReportService:
    def __init__(self, session):
        self.orders = OrderRepository(session)
        self.hubs = HubRepository(session)
        self.menu = MenuRepository(session)

    def hubs_and_brands(self):
        return self.hubs.all(), self.menu.brands()

    def _orders(self, f: ReportFilter) -> list[Order]:
        return self.orders.for_reports(f.start, f.end, f.hub_id)

    # ---- sales ---------------------------------------------------------------------------
    def sales(self, f: ReportFilter) -> Report:
        delivered = [o for o in self._orders(f) if o.status == DELIVERED]
        by_hub, by_brand, by_day = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
        revenue, order_count = 0, 0
        for o in delivered:
            lines = [i for i in o.items if not f.brand_id or i.menu_item.brand_id == f.brand_id]
            if not lines:
                continue
            amount = o.total if not f.brand_id else sum(i.line_total for i in lines)
            revenue += amount
            order_count += 1
            by_hub[o.hub.name][0] += 1
            by_hub[o.hub.name][1] += amount
            by_day[o.created_at.date().isoformat()][0] += 1
            by_day[o.created_at.date().isoformat()][1] += amount
            for i in lines:
                by_brand[i.menu_item.brand.name][1] += i.line_total
            for name in {i.menu_item.brand.name for i in lines}:
                by_brand[name][0] += 1
        average = round(revenue / order_count) if order_count else 0
        rep = Report("Sales report")
        rep.summary = [("Period", f"{f.date_from} to {f.date_to}"), ("Revenue (VND)", f"{revenue:,}"),
                       ("Delivered orders", order_count), ("Average order value (VND)", f"{average:,}")]
        rep.tables = [
            ("By hub", ["Hub", "Orders", "Revenue (VND)"], [(k, v[0], f"{v[1]:,}") for k, v in sorted(by_hub.items())]),
            ("By brand (item amounts)", ["Brand", "Orders", "Revenue (VND)"],
             [(k, v[0], f"{v[1]:,}") for k, v in sorted(by_brand.items())]),
            ("By day", ["Day", "Orders", "Revenue (VND)"], [(k, v[0], f"{v[1]:,}") for k, v in sorted(by_day.items())]),
        ]
        return rep

    # ---- hub workload ----------------------------------------------------------------------
    def workload(self, f: ReportFilter) -> Report:
        orders = self._orders(f)
        hubs = [h for h in self.hubs.all() if not f.hub_id or h.id == f.hub_id]
        days = max(1, (f.date_to - f.date_from).days + 1)
        rep = Report("Hub workload report")
        rep.summary = [("Period", f"{f.date_from} to {f.date_to}"), ("Orders placed", len(orders))]
        summary_rows = []
        for hub in hubs:
            per_hour = defaultdict(int)
            for o in orders:
                if o.hub_id == hub.id:
                    per_hour[o.created_at.hour] += 1
            peak_hour = max(per_hour, key=per_hour.get) if per_hour else None
            peak = per_hour[peak_hour] if peak_hour is not None else 0
            avg_peak = peak / days  # average orders in the busiest hour per day
            pct = round(100 * avg_peak / hub.capacity) if hub.capacity else 0
            summary_rows.append((hub.name, hub.capacity, f"{peak_hour:02d}:00" if peak_hour is not None else "-",
                                 f"{avg_peak:.1f}", f"{pct}%"))
            rep.tables.append((f"Orders per hour: {hub.name}", ["Hour", "Orders", "Average per day"],
                               [(f"{h:02d}:00", per_hour[h], f"{per_hour[h] / days:.1f}") for h in sorted(per_hour)]))
        rep.tables.insert(0, ("Peak hour against capacity",
                              ["Hub", "Capacity", "Busiest hour", "Avg orders in that hour per day", "Against capacity"],
                              summary_rows))
        return rep

    # ---- delivery performance -------------------------------------------------------------------
    def delivery(self, f: ReportFilter) -> Report:
        orders = self._orders(f)
        delivered = [o for o in orders if o.status == DELIVERED and o.confirmed_at and o.delivered_at]
        failed = [o for o in orders if o.status == FAILED]
        minutes = [(o.delivered_at - o.confirmed_at).total_seconds() / 60 for o in delivered]
        late = [m for m in minutes if m > LATE_AFTER_MINUTES]
        attempts = len(delivered) + len(failed)
        rep = Report("Delivery performance report")
        rep.summary = [
            ("Period", f"{f.date_from} to {f.date_to}"),
            ("Delivered orders", len(delivered)),
            ("Average delivery time (minutes, Confirmed to Delivered)", f"{sum(minutes) / len(minutes):.1f}" if minutes else "-"),
            (f"Late deliveries (over {LATE_AFTER_MINUTES} minutes)", f"{len(late)} ({100 * len(late) / len(minutes):.0f}%)" if minutes else "0"),
            ("Failed deliveries", f"{len(failed)} ({100 * len(failed) / attempts:.0f}%)" if attempts else "0"),
        ]
        rows = []
        for hub in [h for h in self.hubs.all() if not f.hub_id or h.id == f.hub_id]:
            m = [(o.delivered_at - o.confirmed_at).total_seconds() / 60 for o in delivered if o.hub_id == hub.id]
            fl = len([o for o in failed if o.hub_id == hub.id])
            rows.append((hub.name, len(m), f"{sum(m) / len(m):.1f}" if m else "-",
                         len([x for x in m if x > LATE_AFTER_MINUTES]), fl))
        rep.tables = [("By hub", ["Hub", "Delivered", "Average minutes", "Late", "Failed"], rows)]
        return rep
