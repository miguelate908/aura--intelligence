"""Pruebas de emisión y validación de tokens JWT (PyJWT, HS256)."""
import base64
import json
import os
from datetime import datetime, timedelta, timezone

os.environ.setdefault("DATABASE_URL", "sqlite://")

import jwt
from fastapi import FastAPI
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.security import ALGORITHM, SECRET_KEY
from database import Base, get_db
import models  # noqa: F401 - registra todas las tablas ORM
from models import Company, User
from routers import auth, customers


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

app = FastAPI()
app.include_router(auth.router)
app.include_router(customers.router)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

EMAIL = "jwt-user@example.com"
PASSWORD = "strong-password-123"


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # El usuario se crea directamente en la base de pruebas para no consumir el límite de registros.
    db = TestingSessionLocal()
    company = Company(name="Empresa JWT")
    db.add(company)
    db.flush()
    db.add(
        User(
            company_id=company.id,
            name="Admin",
            email=EMAIL,
            password_hash=CryptContext(schemes=["bcrypt"], deprecated="auto").hash(PASSWORD),
        )
    )
    db.commit()
    db.close()


def make_token(claims: dict, key: str = SECRET_KEY, algorithm: str = ALGORITHM) -> str:
    return jwt.encode(claims, key, algorithm=algorithm)


def valid_claims(**overrides) -> dict:
    claims = {
        "sub": "1",
        "company_id": 1,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    claims.update(overrides)
    return {k: v for k, v in claims.items() if v is not None}


def get_customers(token: str):
    return client.get("/customers/", headers={"Authorization": f"Bearer {token}"})


def test_login_issues_hs256_token_that_expires_in_30_minutes():
    before = datetime.now(timezone.utc)
    response = client.post("/auth/login", json={"email": EMAIL, "password": PASSWORD})
    assert response.status_code == 200, response.text
    body = response.json()

    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 30 * 60
    assert jwt.get_unverified_header(body["access_token"])["alg"] == "HS256"

    payload = jwt.decode(body["access_token"], SECRET_KEY, algorithms=["HS256"])
    assert payload["sub"] == "1"
    assert payload["company_id"] == 1
    lifetime = datetime.fromtimestamp(payload["exp"], timezone.utc) - before
    assert timedelta(minutes=29) < lifetime <= timedelta(minutes=30, seconds=5)

    assert get_customers(body["access_token"]).status_code == 200


def test_wrong_password_is_rejected():
    response = client.post("/auth/login", json={"email": EMAIL, "password": "wrong-password-123"})
    assert response.status_code == 401


def test_valid_token_is_accepted():
    assert get_customers(make_token(valid_claims())).status_code == 200


def test_expired_token_is_rejected():
    expired = make_token(valid_claims(exp=datetime.now(timezone.utc) - timedelta(seconds=1)))
    response = get_customers(expired)
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_token_without_exp_is_rejected():
    assert get_customers(make_token(valid_claims(exp=None))).status_code == 401


def test_token_without_sub_is_rejected():
    assert get_customers(make_token(valid_claims(sub=None))).status_code == 401


def test_token_with_non_numeric_sub_is_rejected():
    assert get_customers(make_token(valid_claims(sub="admin"))).status_code == 401


def test_token_for_unknown_user_is_rejected():
    assert get_customers(make_token(valid_claims(sub="999"))).status_code == 401


def test_token_signed_with_another_key_is_rejected():
    forged = make_token(valid_claims(), key="otra-clave-distinta-de-al-menos-32-caracteres")
    assert get_customers(forged).status_code == 401


def test_token_with_another_hmac_algorithm_is_rejected():
    assert get_customers(make_token(valid_claims(), algorithm="HS512")).status_code == 401


def test_unsigned_alg_none_token_is_rejected():
    def b64(data: dict) -> str:
        return base64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b"=").decode()

    claims = valid_claims()
    claims["exp"] = int(claims["exp"].timestamp())
    unsigned = f"{b64({'alg': 'none', 'typ': 'JWT'})}.{b64(claims)}."
    assert get_customers(unsigned).status_code == 401


def test_tampered_payload_is_rejected():
    header, _, signature = make_token(valid_claims()).split(".")
    tampered_claims = valid_claims(sub="2")
    tampered_claims["exp"] = int(tampered_claims["exp"].timestamp())
    tampered_payload = base64.urlsafe_b64encode(json.dumps(tampered_claims).encode()).rstrip(b"=").decode()
    assert get_customers(f"{header}.{tampered_payload}.{signature}").status_code == 401


def test_malformed_and_missing_tokens_are_rejected():
    assert get_customers("no-es-un-jwt").status_code == 401
    assert client.get("/customers/").status_code == 401


def test_required_check_blocks_merge():
    raise AssertionError("Fallo deliberado para verificar la protección de master")
