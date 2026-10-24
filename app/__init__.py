"""SaigonBite Flask application package."""

import os

from flask import Flask, jsonify

from app.controller.orders import orders_bp
from app.controller.vouchers import reports_bp, vouchers_bp
from app.data.database import init_database


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, template_folder="view/templates", static_folder="view/static")
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "local-development-only"),
        DATABASE_URL=os.environ.get("DATABASE_URL", "sqlite:///saigonbite.db"),
    )
    if test_config:
        app.config.update(test_config)

    init_database(app)
    app.register_blueprint(orders_bp)
    app.register_blueprint(vouchers_bp)
    app.register_blueprint(reports_bp)

    @app.get("/")
    def index():
        return jsonify({"name": "SaigonBite", "status": "ready"})

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return app
