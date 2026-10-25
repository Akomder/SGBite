"""Login, roles and language. Layer: CONTROLLER."""
from __future__ import annotations

from functools import wraps

from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for

from ..data.database import get_session
from ..data.repositories import UserRepository

bp = Blueprint("auth", __name__)
HOME = {"customer": "ordering.choose_hub", "kitchen": "kitchen.dashboard",
        "admin": "vouchers.list_vouchers", "manager": "reports.index"}


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if g.user is None:
                flash("Please log in first.", "error")
                return redirect(url_for("auth.login", next=request.path))
            if g.user.role not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator


@bp.before_app_request
def load_user():
    user_id = session.get("user_id")
    g.user = UserRepository(get_session()).get(user_id) if user_id else None


@bp.get("/")
def home():
    if g.user is None:
        return redirect(url_for("auth.login"))
    return redirect(url_for(HOME[g.user.role]))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = UserRepository(get_session()).by_username(request.form.get("username", "").strip())
        if user and user.check_password(request.form.get("password", "")):
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("auth.home"))
        flash("Wrong username or password.", "error")
    return render_template("login.html")


@bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@bp.get("/lang/<code>")
def set_lang(code):
    if code in ("en", "vi"):
        session["lang"] = code
    return redirect(request.referrer or url_for("auth.home"))
