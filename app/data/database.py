"""Database set-up. Layer: DATA ACCESS."""
from __future__ import annotations

import time

from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

from ..domain.models import Base


class Database:
    def __init__(self, url: str):
        kwargs = {}
        if url.startswith("sqlite") and (url in ("sqlite://", "sqlite:///:memory:")):
            kwargs = {"poolclass": StaticPool, "connect_args": {"check_same_thread": False}}
        self.engine = create_engine(url, future=True, **kwargs)
        self.session = scoped_session(sessionmaker(bind=self.engine, expire_on_commit=False))

    def create_tables(self, retries: int = 30) -> None:
        for attempt in range(retries):
            try:
                Base.metadata.create_all(self.engine)
                return
            except OperationalError:
                if attempt == retries - 1:
                    raise
                time.sleep(1)  # database container may still be starting

    def drop_tables(self) -> None:
        Base.metadata.drop_all(self.engine)


def init_app(app) -> Database:
    db = Database(app.config["DATABASE_URL"])
    app.extensions["db"] = db

    @app.teardown_appcontext
    def _remove_session(_exc):
        db.session.remove()

    return db


def get_session():
    return current_app.extensions["db"].session
