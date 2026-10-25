"""UC4 Produce management reports. Layer: CONTROLLER (owner 523V0017)."""
from __future__ import annotations

import csv
import io

from flask import Blueprint, Response, flash, redirect, render_template, request, url_for

from ..data.database import get_session
from ..domain.errors import DomainError
from ..domain.reports import ReportFilter, ReportService
from .auth import role_required

bp = Blueprint("reports", __name__, url_prefix="/reports")
KINDS = {"sales": "sales", "workload": "workload", "delivery": "delivery"}


def _service():
    return ReportService(get_session())


@bp.get("")
@role_required("manager")
def index():
    hubs, brands = _service().hubs_and_brands()
    return render_template("reports_index.html", hubs=hubs, brands=brands)


@bp.get("/<kind>")
@role_required("manager")
def show(kind):
    if kind not in KINDS:
        return redirect(url_for("reports.index"))
    svc = _service()
    try:
        f = ReportFilter.parse(request.args)
        report = getattr(svc, kind)(f)
    except DomainError as e:
        flash(str(e), "error")
        return redirect(url_for("reports.index"))
    if request.args.get("format") == "csv":
        buf = io.StringIO()
        csv.writer(buf).writerows(report.csv_rows())
        return Response("\ufeff" + buf.getvalue(), mimetype="text/csv",
                        headers={"Content-Disposition": f"attachment; filename={kind}_report.csv"})
    hubs, brands = svc.hubs_and_brands()
    return render_template("report.html", report=report, kind=kind, f=f, hubs=hubs, brands=brands, args=request.args)
