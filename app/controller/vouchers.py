"""UC3 Manage vouchers. Layer: CONTROLLER (owner 523K0076)."""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..data.database import get_session
from ..domain.errors import DomainError
from ..domain.vouchers import STATES, VoucherService
from .auth import role_required

bp = Blueprint("vouchers", __name__, url_prefix="/admin/vouchers")


def _service():
    return VoucherService(get_session())


@bp.get("")
@role_required("admin")
def list_vouchers():
    text, state = request.args.get("q", ""), request.args.get("state", "")
    return render_template("voucher_list.html", rows=_service().list(text, state), q=text, state=state, states=STATES)


@bp.route("/new", methods=["GET", "POST"])
@role_required("admin")
def create_voucher():
    if request.method == "POST":
        try:
            _service().create(request.form)
            flash("Voucher created.", "ok")
            return redirect(url_for("vouchers.list_vouchers"))
        except DomainError as e:
            flash(str(e), "error")
    return render_template("voucher_form.html", voucher=None, form=request.form)


@bp.route("/<int:voucher_id>/edit", methods=["GET", "POST"])
@role_required("admin")
def edit_voucher(voucher_id):
    svc = _service()
    try:
        voucher = svc.get(voucher_id)
        if request.method == "POST":
            svc.update(voucher_id, request.form)
            flash("Voucher updated.", "ok")
            return redirect(url_for("vouchers.list_vouchers"))
    except DomainError as e:
        flash(str(e), "error")
        if request.method == "GET":
            return redirect(url_for("vouchers.list_vouchers"))
    return render_template("voucher_form.html", voucher=voucher, form=request.form if request.method == "POST" else None)


@bp.post("/<int:voucher_id>/deactivate")
@role_required("admin")
def deactivate(voucher_id):
    try:
        _service().deactivate(voucher_id)
        flash("Voucher deactivated. Past orders keep it.", "ok")
    except DomainError as e:
        flash(str(e), "error")
    return redirect(url_for("vouchers.list_vouchers"))
