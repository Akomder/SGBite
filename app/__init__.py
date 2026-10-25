"""SaigonBite OFDH prototype: Flask application factory.

Layers: view (templates) -> controller (blueprints) -> domain (models, services) -> data (repositories).
"""
from __future__ import annotations

import os

import click
from flask import Flask, g, session

from .data import database
from .data.seed import seed
from .view.i18n import status_label, translate


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, template_folder="view/templates", static_folder="view/static")
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        DATABASE_URL=os.environ.get("DATABASE_URL", "sqlite:///saigonbite.db"),
        PASSWORD_HASH_METHOD="pbkdf2:sha256",
    )
    if test_config:
        app.config.update(test_config)

    db = database.init_app(app)

    from .controller import auth, kitchen, ordering, reports, vouchers
    for module in (auth, ordering, kitchen, vouchers, reports):
        app.register_blueprint(module.bp)

    def current_lang() -> str:
        user = getattr(g, "user", None)
        default = "vi" if (user and user.customer_type == "local") else "en"
        return session.get("lang", default)

    @app.context_processor
    def inject():
        lang = current_lang()
        return {"user": getattr(g, "user", None), "lang": lang,
                "t": lambda key: translate(lang, key),
                "status_label": lambda s: status_label(lang, s)}

    @app.template_filter("vnd")
    def vnd(amount):
        return f"{int(amount):,} VND"

    @app.errorhandler(403)
    def forbidden(_e):
        return "You are not allowed to open this page.", 403

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.cli.command("init-db")
    @click.option("--no-demo", is_flag=True, help="Do not create demo orders.")
    def init_db(no_demo):
        """Create tables and add sample data when the database is empty."""
        db.create_tables()
        added = seed(db, app.config["PASSWORD_HASH_METHOD"], demo_orders=not no_demo)
        click.echo("Sample data added." if added else "Database already has data.")

    return app
