"""UC1 Place an order. Layer: CONTROLLER (owner 523K0076)."""
from __future__ import annotations

from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from ..data.database import get_session
from ..domain.errors import DomainError, HubFullError, ValidationError
from ..domain.ordering import OrderingService
from .auth import role_required

bp = Blueprint("ordering", __name__)


def _service():
    return OrderingService(get_session())


def _read_form(menu):
    """Collect what the customer typed so the form can be shown again after an error."""
    quantities = {}
    for item in menu:
        raw = (request.form.get(f"qty_{item.id}") or "0").strip() or "0"
        try:
            quantities[item.id] = int(raw)
        except ValueError:
            raise ValidationError("Quantities must be whole numbers.")
        if quantities[item.id] < 0:
            raise ValidationError("Quantities cannot be negative.")
    return quantities


def _form_values():
    return {"address": request.form.get("address", ""), "distance_km": request.form.get("distance_km", ""),
            "voucher": request.form.get("voucher", ""), "payment": request.form.get("payment", ""),
            "qty": {k[4:]: v for k, v in request.form.items() if k.startswith("qty_")}}


@bp.get("/order")
@role_required("customer")
def choose_hub():
    return render_template("choose_hub.html", statuses=_service().hub_overview())


@bp.get("/order/hub/<int:hub_id>")
@role_required("customer")
def order_form(hub_id):
    svc = _service()
    try:
        hub = svc.get_hub(hub_id)
    except DomainError as e:
        flash(str(e), "error")
        return redirect(url_for("ordering.choose_hub"))
    return _render_form(svc, hub, {})


def _render_form(svc, hub, form, suggestions=None):
    status = svc.hub_status(hub)
    if suggestions is None and status.state == "busy":
        suggestions = svc._suggestions(hub)
    return render_template("order_form.html", hub=hub, status=status, menu=svc.menu_for(hub.id), form=form,
                           payments=svc.allowed_payments(g.user), suggestions=suggestions or [])


def _handle(hub_id, action):
    svc = _service()
    try:
        hub = svc.get_hub(hub_id)
    except DomainError as e:
        flash(str(e), "error")
        return redirect(url_for("ordering.choose_hub"))
    try:
        quantities = _read_form(svc.menu_for(hub_id))
        args = (g.user, hub_id, quantities, request.form.get("distance_km"), request.form.get("address"),
                request.form.get("voucher"), request.form.get("payment"))
        if action == "preview":
            quote = svc.quote(*args)
            return render_template("order_preview.html", q=quote, form=_form_values(), hub=hub)
        order = svc.place(*args)
        flash("Your order was placed.", "ok")
        return redirect(url_for("ordering.order_detail", order_id=order.id))
    except HubFullError as e:
        flash(str(e), "error")
        return _render_form(svc, hub, _form_values(), e.suggestions)
    except DomainError as e:
        flash(str(e), "error")
        return _render_form(svc, hub, _form_values())


@bp.post("/order/hub/<int:hub_id>/preview")
@role_required("customer")
def preview(hub_id):
    return _handle(hub_id, "preview")


@bp.post("/order/hub/<int:hub_id>/place")
@role_required("customer")
def place(hub_id):
    return _handle(hub_id, "place")


@bp.get("/orders")
@role_required("customer")
def my_orders():
    return render_template("my_orders.html", orders=_service().my_orders(g.user))


@bp.get("/orders/<int:order_id>")
@role_required("customer")
def order_detail(order_id):
    svc = _service()
    try:
        order = svc.get_order(g.user, order_id)
    except DomainError as e:
        flash(str(e), "error")
        return redirect(url_for("ordering.my_orders"))
    return render_template("order_detail.html", order=order, notes=svc.notifications_for(g.user))


@bp.post("/orders/<int:order_id>/cancel")
@role_required("customer")
def cancel(order_id):
    try:
        _service().cancel(g.user, order_id)
        flash("Order cancelled.", "ok")
    except DomainError as e:
        flash(str(e), "error")
    return redirect(url_for("ordering.order_detail", order_id=order_id))
