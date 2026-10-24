"""SQLAlchemy engine and session setup."""
from collections.abc import Iterator
from contextlib import contextmanager

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def init_database(app: Flask) -> None:
    # Import model declarations before create_all registers the mapped tables.
    from app.data import models  # noqa: F401

    url = app.config["DATABASE_URL"]
    options = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=options, pool_pre_ping=True)
    app.extensions["saigonbite_engine"] = engine
    app.extensions["saigonbite_session_factory"] = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(engine)


@contextmanager
def session_scope(app: Flask) -> Iterator[Session]:
    session = app.extensions["saigonbite_session_factory"]()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
