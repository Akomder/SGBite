import pytest

from app import create_app
from app.data.database import get_session
from app.data.repositories import (HubRepository, MenuRepository, OrderRepository, UserRepository,
                                   VoucherRepository)
from app.data.seed import seed

FAST_HASH = "pbkdf2:sha256:1000"


@pytest.fixture
def app():
    app = create_app({"TESTING": True, "DATABASE_URL": "sqlite://", "PASSWORD_HASH_METHOD": FAST_HASH,
                      "SECRET_KEY": "test"})
    db = app.extensions["db"]
    db.create_tables()
    seed(db, FAST_HASH, demo_orders=False)
    yield app
    db.session.remove()
    db.drop_tables()


@pytest.fixture
def session(app):
    with app.app_context():
        yield get_session()


@pytest.fixture
def client(app):
    return app.test_client()


class Login:
    def __init__(self, client):
        self.client = client

    def __call__(self, username, password="password"):
        return self.client.post("/login", data={"username": username, "password": password}, follow_redirects=True)


@pytest.fixture
def login(client):
    return Login(client)


@pytest.fixture
def users(session):
    repo = UserRepository(session)
    return {n: repo.by_username(n) for n in ("an", "tourist", "kitchen1", "kitchen2", "admin", "manager")}


@pytest.fixture
def hubs(session):
    return HubRepository(session).all()


@pytest.fixture
def items(session, hubs):
    return {m.name_en: m for m in MenuRepository(session).available_items(hubs[0].id)}


@pytest.fixture
def make_order(session, users, hubs, items):
    """Place an order through the real UC1 service."""
    from app.domain.ordering import OrderingService

    def _make(customer="an", hub=0, qty=2, item="Rare beef pho", distance=3.0, voucher="", payment=None, **kw):
        cust = users[customer]
        pay = payment or ("ewallet" if cust.customer_type == "local" else "card")
        svc = OrderingService(session)
        return svc.place(cust, hubs[hub].id, {items[item].id: qty}, distance, "1 Test Street", voucher, pay, **kw)
    return _make
