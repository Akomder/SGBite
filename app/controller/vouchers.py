"""HTTP endpoints for voucher maintenance and reporting."""
from decimal import Decimal, InvalidOperation

from flask import Blueprint, current_app, jsonify, request

from app.data.database import session_scope
from app.data.models import Voucher
from app.data.repositories import OrderRepository, VoucherRepository
from app.domain.vouchers import validate_voucher

vouchers_bp = Blueprint("vouchers", __name__, url_prefix="/vouchers")
reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@vouchers_bp.get("")
def list_vouchers():
    with session_scope(current_app) as session:
        rows = VoucherRepository(session).list_all()
        return jsonify([{"id": v.id, "code": v.code, "discount_percent": str(v.discount_percent), "active": v.active} for v in rows])


@vouchers_bp.post("")
def create_voucher():
    payload = request.get_json(silent=True) or {}
    try:
        code = str(payload.get("code", ""))
        discount = Decimal(str(payload.get("discount_percent", "0")))
        validate_voucher(code, discount)
        with session_scope(current_app) as session:
            voucher = Voucher(code=code.strip().upper(), description=str(payload.get("description", "")), discount_percent=discount)
            session.add(voucher)
            session.flush()
            result = {"id": voucher.id, "code": voucher.code, "discount_percent": str(voucher.discount_percent)}
        return jsonify(result), 201
    except (ValueError, InvalidOperation) as error:
        return jsonify({"error": str(error)}), 400


@reports_bp.get("/summary")
def summary():
    with session_scope(current_app) as session:
        count = OrderRepository(session).count_orders()
    return jsonify({"order_count": count})
