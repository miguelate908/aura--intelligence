import os

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-that-is-long-enough-32-characters")

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
import models  # noqa: F401
from routers import auth, customers, imports, products

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SessionTest = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

app = FastAPI()
for r in (auth.router, customers.router, products.router, imports.router):
    app.include_router(r)


def override_get_db():
    db = SessionTest()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function():
    os.environ["DISABLE_RATE_LIMIT"] = "1"  # registra varias empresas seguidas
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function():
    os.environ.pop("DISABLE_RATE_LIMIT", None)


def token(company: str, email: str) -> dict:
    body = {"company_name": company, "name": "Admin", "email": email, "password": "strong-password-123"}
    assert client.post("/auth/register", json=body).status_code == 200
    t = client.post("/auth/login", json={"email": email, "password": body["password"]}).json()["access_token"]
    return {"Authorization": f"Bearer {t}"}


def test_import_requires_auth():
    assert client.post("/import/customers", json={"rows": [{"name": "X"}]}).status_code == 401


def test_import_creates_rows_only_for_own_company():
    a = token("Empresa A", "a@example.com")
    b = token("Empresa B", "b@example.com")
    rows = [{"name": "Cliente 1", "email": "c1@example.com"}, {"name": " Cliente 2 ", "phone": "", "company_id": 2}]
    r = client.post("/import/customers", headers=a, json={"rows": rows})
    assert r.status_code == 200, r.text
    assert r.json() == {"imported": 2}
    names = sorted(c["name"] for c in client.get("/customers/", headers=a).json())
    assert names == ["Cliente 1", "Cliente 2"]
    assert client.get("/customers/", headers=b).json() == []


def test_import_is_all_or_nothing_and_reports_rows():
    a = token("Empresa A", "a@example.com")
    rows = [
        {"sku": "A1", "name": "Uno", "price": "1.500,5".replace(".", "")},
        {"sku": "A1", "name": "Repetido", "price": "2"},
        {"sku": "B2", "name": "", "price": "3"},
        {"sku": "C3", "name": "Negativo", "price": "-1"},
    ]
    r = client.post("/import/products", headers=a, json={"rows": rows})
    assert r.status_code == 422
    assert [e["row"] for e in r.json()["detail"]["errors"]] == [2, 3, 4]
    assert client.get("/products/", headers=a).json() == []

    ok = client.post("/import/products", headers=a, json={"rows": rows[:1]})
    assert ok.status_code == 200, ok.text
    assert client.get("/products/", headers=a).json()[0]["price"] == 1500.5
    dup = client.post("/import/products", headers=a, json={"rows": rows[:1]})
    assert dup.status_code == 422


def test_unknown_entity_is_rejected():
    a = token("Empresa A", "a@example.com")
    assert client.post("/import/users", headers=a, json={"rows": [{"name": "x"}]}).status_code == 404
