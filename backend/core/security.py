import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from database import get_db
from models import User


ALGORITHM = "HS256"
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise RuntimeError("JWT_SECRET_KEY debe estar configurada con al menos 32 caracteres")

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Autenticación requerida o token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub", ""))
    except (JWTError, TypeError, ValueError):
        raise unauthorized

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise unauthorized
    return user


def require_company_access(company_id: int, user: User) -> None:
    if company_id != user.company_id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta empresa")
