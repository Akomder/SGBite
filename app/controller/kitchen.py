"""UC2 Confirm or reject an incoming order. Layer: CONTROLLER (owner 523V0017)."""
from __future__ import annotations

from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from ..data.database import get_session
from ..domain.errors import DomainError
from ..domain.kitchen import KitchenService
from .auth import role_required

bp = Blueprint("kitchen", __name__, url_prefix="/kitchen")


def _service():
    return KitchenService(get_session())


@bp.get("")
@role_required("kitchen")
def dashboard():
    svc = _service()
    return render_template("kitchen.html", status=svc.hub_status(g.user),
                           incoming=svc.incoming_orders(g.user), in_progress=svc.in_progress_orders(g.user))


def _act(fn, ok_message):
    try:
        fn()
        flash(ok_message, "ok")
    except DomainError as e:
        flash(str(e), "error")
    return redirect(url_for("kitchen.dashboard"))


@bp.post("/orders/<int:order_id>/confirm")
@role_required("kitchen")
def confirm(order_id):
    return _act(lambda: _service().confirm(g.user, order_id), "Order confirmed.")


@bp.post("/orders/<int:order_id>/reject")
@role_required("kitchen")
def reject(order_id):
    return _act(lambda: _service().reject(g.user, order_id, request.form.get("reason", "")), "Order rejected.")


@bp.post("/orders/<int:order_id>/advance")
@role_required("kitchen")
def advance(order_id):
    return _act(lambda: _service().advance(g.user, order_id, request.form.get("status", "")), "Order updated.")
