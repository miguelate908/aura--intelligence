from datetime import datetime, timedelta, timezone

from jose import jwt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import get_db
from models import User, Company
from schemas import LoginRequest, UserCreate
from core.security import ALGORITHM, SECRET_KEY


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.post("/register")
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
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

    try:
        company = Company(name=user.company_name)
        db.add(company)
        db.flush()
        new_user = User(
            company_id=company.id,
            name=user.name,
            email=user.email,
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
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == credentials.email)
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

