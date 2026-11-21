import threading
import time

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from core.security import get_current_user
from database import get_db
from models import User
from routers.auth import pwd_context

router = APIRouter(prefix="/account", tags=["Account"])

MAX_FAILS = 5  # intentos fallidos por usuario cada 15 minutos
_fails: dict[int, list[float]] = {}
_lock = threading.Lock()


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=12, max_length=72)

    @field_validator("new_password")
    @classmethod
    def fits_bcrypt(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("La contraseña no puede superar 72 bytes en UTF-8")
        return v


def _recent_fails(uid: int) -> list[float]:
    now = time.time()
    return [t for t in _fails.get(uid, []) if now - t < 900]


@router.post("/password", status_code=204)
def change_password(body: PasswordChange, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    with _lock:
        recent = _recent_fails(current_user.id)
        if len(recent) >= MAX_FAILS:
            raise HTTPException(status_code=429, detail="Demasiados intentos. Inténtalo en unos minutos.")
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user or not pwd_context.verify(body.current_password, user.password_hash):
        with _lock:
            _fails[current_user.id] = _recent_fails(current_user.id) + [time.time()]
        raise HTTPException(status_code=400, detail="La contraseña actual no es correcta")
    if body.current_password == body.new_password:
        raise HTTPException(status_code=422, detail="La nueva contraseña debe ser distinta de la actual")
    user.password_hash = pwd_context.hash(body.new_password)
    db.commit()
    with _lock:
        _fails.pop(current_user.id, None)
    return Response(status_code=204)
