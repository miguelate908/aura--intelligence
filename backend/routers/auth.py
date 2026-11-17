import os
from datetime import datetime, timedelta, timezone

from jose import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import get_db
from models import User, Company
from schemas import LoginRequest, UserCreate
from core.security import ALGORITHM, SECRET_KEY
from core.ratelimit import RateLimiter, client_ip


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Límites: registro por IP; login por IP y por correo.
register_limit = RateLimiter(max_hits=5, window_seconds=3600)
login_ip_limit = RateLimiter(max_hits=20, window_seconds=900)
login_email_limit = RateLimiter(max_hits=8, window_seconds=900)


def registration_enabled() -> bool:
    # En producción las cuentas de clientes se crean con scripts/create_client.py.
    return os.getenv("REGISTRATION_ENABLED", "true").strip().lower() in {"1", "true", "yes"}


@router.get("/config")
def auth_config():
    return {"registration_enabled": registration_enabled()}


@router.post("/register")
def register_user(
    user: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    if not registration_enabled():
        raise HTTPException(status_code=403, detail="El registro público está desactivado. Solicita una demostración.")
    register_limit.hit(client_ip(request))
    email = user.email.strip().lower()
    existing_user = (
        db.query(User)
        .filter(func.lower(User.email) == email)
        .first()
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado"
        )

    password_hash = pwd_context.hash(user.password)

    try:
        company = Company(name=user.company_name)
        db.add(company)
        db.flush()
        new_user = User(
            company_id=company.id,
            name=user.name,
            email=email,
            password_hash=password_hash,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception:
        db.rollback()
        raise

    return {
        "id": new_user.id,
        "company_id": new_user.company_id,
        "name": new_user.name,
        "email": new_user.email,
        "created_at": new_user.created_at
    }


@router.post("/login")
def login_user(
    credentials: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    email = credentials.email.strip().lower()
    ip = client_ip(request)
    login_ip_limit.hit(ip)
    login_email_limit.hit(f"{ip}|{email}")
    user = (
        db.query(User)
        .filter(func.lower(User.email) == email)
        .first()
    )

    if user is None or not pwd_context.verify(
        credentials.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    token = jwt.encode(
        {
            "sub": str(user.id),
            "company_id": user.company_id,
            "exp": expire
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

