"""HTTP endpoints for order placement and hub decisions."""
from flask import Blueprint, current_app, jsonify, request

from app.data.database import session_scope
from app.data.repositories import OrderRepository
from app.domain.orders import confirm_order, create_order, reject_order

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")


@orders_bp.post("")
def place_order():
    payload = request.get_json(silent=True) or {}
    try:
        order = create_order(str(payload.get("customer_name", "")), str(payload.get("delivery_address", "")), payload.get("items", []))
        with session_scope(current_app) as session:
            order = OrderRepository(session).add(order)
            result = {"id": order.id, "status": order.status, "total_amount": str(order.total_amount)}
        return jsonify(result), 201
    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400


@orders_bp.post("/<int:order_id>/decision")
def decide_order(order_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        with session_scope(current_app) as session:
            order = OrderRepository(session).get(order_id)
            if order is None:
                return jsonify({"error": "Order not found."}), 404
            if payload.get("decision") == "confirm":
                confirm_order(order)
            elif payload.get("decision") == "reject":
                reject_order(order, str(payload.get("reason", "")))
            else:
                return jsonify({"error": "Decision must be 'confirm' or 'reject'."}), 400
            result = {"id": order.id, "status": order.status, "rejection_reason": order.rejection_reason}
        return jsonify(result)
    except ValueError as error:
        return jsonify({"error": str(error)}), 409
