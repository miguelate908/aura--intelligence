from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import get_db
from models import User, Company
from schemas import UserCreate

import os
from datetime import datetime, timedelta, timezone

from jose import jwt
from jose.exceptions import JWTError
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "Falta configurar JWT_SECRET_KEY en el archivo .env"
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



@router.post("/register")
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    company = (
        db.query(Company)
        .filter(Company.id == user.company_id)
        .first()
    )

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada"
        )

    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado"
        )

    password_hash = pwd_context.hash(user.password)

    new_user = User(
        company_id=user.company_id,
        name=user.name,
        email=user.email,
        password_hash=password_hash
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "company_id": new_user.company_id,
        "name": new_user.name,
        "email": new_user.email,
        "created_at": new_user.created_at
    }
@router.post("/login")
def login_user(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if user is None or not pwd_context.verify(
        password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
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