import os

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
import models  # noqa: F401 - registers all ORM tables on Base.metadata
from routers import assistant, auth, companies, customers, events, graph, products, query, relationships, warehouses


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)

app = FastAPI()
for router in (
    companies.router,
    customers.router,
    products.router,
    warehouses.router,
    events.router,
    query.router,
    relationships.router,
    graph.router,
    auth.router,
    assistant.router,
):
    app.include_router(router)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function():
    # Cada prueba parte sin intentos acumulados: el límite de registro por IP es de 5 por hora.
    for limiter in (auth.register_limit, auth.login_ip_limit, auth.login_email_limit):
        limiter._hits.clear()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def register(company_name: str, email: str) -> str:
    response = client.post(
        "/auth/register",
        json={
            "company_name": company_name,
            "name": "Admin",
            "email": email,
            "password": "strong-password-123",
        },
    )
    assert response.status_code == 200, response.text
    login = client.post(
        "/auth/login",
        json={"email": email, "password": "strong-password-123"},
    )
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


def test_data_routes_require_a_valid_bearer_token():
    missing_token = client.get("/customers/")
    invalid_token = client.get(
        "/customers/",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )

    assert missing_token.status_code == 401
    assert invalid_token.status_code == 401


def test_registration_validates_email_and_password():
    invalid_user = client.post(
        "/auth/register",
        json={
            "company_name": "Empresa",
            "name": "Admin",
            "email": "no-es-un-correo",
            "password": "corta",
        },
    )

    assert invalid_user.status_code == 422


def test_passwords_over_bcrypt_utf8_limit_are_rejected_for_register_and_login():
    passwords = ("é" * 40, "é" * 36 + "A" + "X" * 3)
    assert all(len(password) <= 72 for password in passwords)
    assert all(len(password.encode("utf-8")) > 72 for password in passwords)
    assert passwords[0].encode("utf-8")[:72] == passwords[1].encode("utf-8")[:72]

    for index, password in enumerate(passwords):
        registration = client.post(
            "/auth/register",
            json={
                "company_name": "Empresa",
                "name": "Admin",
                "email": f"unicode-password-{index}@example.com",
                "password": password,
            },
        )
        login = client.post(
            "/auth/login",
            json={"email": f"unicode-password-{index}@example.com", "password": password},
        )

        assert registration.status_code == 422
        assert login.status_code == 422


def test_user_can_only_read_and_write_data_for_their_company():
    token_a = register("Empresa A", "admin-a@example.com")
    token_b = register("Empresa B", "admin-b@example.com")

    with_a = {"Authorization": f"Bearer {token_a}"}
    with_b = {"Authorization": f"Bearer {token_b}"}
    create_a = client.post(
        "/customers/",
        headers=with_a,
        json={"company_id": 1, "name": "Cliente A"},
    )
    assert create_a.status_code == 200, create_a.text
    assert "id" in create_a.json(), create_a.text
    customer_id = create_a.json()["id"]

    denied_create = client.post(
        "/customers/",
        headers=with_b,
        json={"company_id": 1, "name": "Intruso"},
    )
    hidden_customer = client.get(f"/customers/{customer_id}", headers=with_b)
    other_company_events = client.get("/events/company/1", headers=with_b)
    other_company_summary = client.get("/query/company/1", headers=with_b)
    other_company_graph = client.get("/graph/entity/company/1", headers=with_b)

    assert denied_create.status_code == 403
    assert hidden_customer.status_code == 404
    assert other_company_events.status_code == 403
    assert other_company_summary.status_code == 403
    assert other_company_graph.status_code == 200
    assert other_company_graph.json()["nodes"] == []
    assert other_company_graph.json()["relationships"] == []

    own_customers = client.get("/customers/", headers=with_b)
    assert own_customers.status_code == 200
    assert own_customers.json() == []


def test_assistant_chat_returns_response_and_only_uses_users_company_data():
    token_a = register("Empresa A", "assistant-a@example.com")
    token_b = register("Empresa B", "assistant-b@example.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    created = client.post(
        "/customers/",
        headers=headers_a,
        json={"company_id": 1, "name": "Cliente Confidencial A"},
    )
    assert created.status_code == 200, created.text

    response_a = client.post("/assistant/chat", headers=headers_a, json={"message": "resumen de mi empresa"})
    response_b = client.post("/assistant/chat", headers=headers_b, json={"message": "resumen de mi empresa"})
    customers_a = client.post("/assistant/chat", headers=headers_a, json={"message": "lista de clientes"})
    customers_b = client.post("/assistant/chat", headers=headers_b, json={"message": "lista de clientes"})

    assert response_a.status_code == 200, response_a.text
    assert response_a.json()["intent"] == "summary"
    assert "Empresa A" in response_a.json()["reply"]
    assert "Cliente Confidencial A" not in response_a.json()["reply"]
    assert response_b.status_code == 200, response_b.text
    assert response_b.json()["intent"] == "summary"
    assert "Empresa B" in response_b.json()["reply"]
    assert "Cliente Confidencial A" not in response_b.json()["reply"]
    assert customers_a.status_code == 200, customers_a.text
    assert "Cliente Confidencial A" in customers_a.json()["reply"]
    assert customers_b.status_code == 200, customers_b.text
    assert "Cliente Confidencial A" not in customers_b.json()["reply"]


def test_assistant_data_quality_flags_issues_only_for_own_company():
    token_a = register("Empresa A", "quality-a@example.com")
    token_b = register("Empresa B", "quality-b@example.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    for body in (
        {"company_id": 1, "name": "Ana Pérez", "email": "ana@example.com"},
        {"company_id": 1, "name": "ana pérez ", "email": "ANA@example.com"},
        {"company_id": 1, "name": "Sin Contacto"},
    ):
        assert client.post("/customers/", headers=headers_a, json=body).status_code == 200
    for body in (
        {"company_id": 1, "sku": "SKU-1", "name": "Uno", "price": 10},
        {"company_id": 1, "sku": "sku-1", "name": "Dos", "price": 0},
    ):
        assert client.post("/products/", headers=headers_a, json=body).status_code == 200

    reply_a = client.post("/assistant/chat", headers=headers_a, json={"message": "Revisa la calidad de mis datos"})
    reply_b = client.post("/assistant/chat", headers=headers_b, json={"message": "¿tengo clientes duplicados?"})

    assert reply_a.status_code == 200, reply_a.text
    assert reply_a.json()["intent"] == "quality"
    text = reply_a.json()["reply"]
    assert "1 de 3 cliente(s) sin correo ni teléfono" in text
    assert "Correo repetido en 2 clientes: ana@example.com" in text
    assert "Nombre de cliente repetido 2 veces" in text
    assert "1 de 2 producto(s) con precio 0" in text
    assert "SKU repetido en 2 productos: sku-1" in text

    assert reply_b.status_code == 200, reply_b.text
    assert reply_b.json()["intent"] == "quality"
    assert "Todavía no hay datos que revisar" in reply_b.json()["reply"]
    assert "ana" not in reply_b.json()["reply"].lower()
