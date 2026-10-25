import logging
import os
import re
import smtplib
import ssl
import time
from collections import deque
from email.message import EmailMessage
from threading import Lock
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.orm import Session

from core.security import get_current_user
from database import get_db
from models import DemoRequest, User


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/demo-requests", tags=["Demo requests"])

SECTORS = {"logistica", "retail", "manufactura", "tecnologia", "servicios", "datos", "otro"}
RATE_LIMIT = 5
RATE_WINDOW_SECONDS = 10 * 60
_request_times: dict[str, deque[float]] = {}
_rate_lock = Lock()
_last_cleanup = 0.0


class DemoRequestCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=150)
    email: str = Field(min_length=3, max_length=254, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    company: str = Field(min_length=1, max_length=150)
    job_title: str = Field(min_length=1, max_length=150)
    sector: str = Field(max_length=50)
    company_size: Optional[str] = Field(default=None, max_length=50)
    need: str = Field(min_length=10, max_length=2000)
    message: str = Field(default="", max_length=2000)
    consent: bool
    website: str = Field(default="", max_length=200)

    @field_validator("name", "company", "job_title")
    @classmethod
    def reject_control_characters(cls, value: str) -> str:
        if any(ord(char) < 32 for char in value):
            raise ValueError("El campo contiene caracteres no permitidos")
        return value

    @field_validator("sector")
    @classmethod
    def valid_sector(cls, value: str) -> str:
        if value not in SECTORS:
            raise ValueError("Sector no válido")
        return value


def _enforce_rate_limit(request: Request) -> None:
    global _last_cleanup
    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()

    with _rate_lock:
        attempts = _request_times.setdefault(client_ip, deque())
        while attempts and now - attempts[0] >= RATE_WINDOW_SECONDS:
            attempts.popleft()
        if len(attempts) >= RATE_LIMIT:
            retry_after = max(1, int(RATE_WINDOW_SECONDS - (now - attempts[0])))
            raise HTTPException(
                status_code=429,
                detail="Se alcanzó el límite de solicitudes. Inténtalo más tarde.",
                headers={"Retry-After": str(retry_after)},
            )
        attempts.append(now)

        if now - _last_cleanup >= 60:
            expired = [ip for ip, values in _request_times.items() if not values or now - values[-1] >= RATE_WINDOW_SECONDS]
            for ip in expired:
                _request_times.pop(ip, None)
            _last_cleanup = now


def _send_notification(demo: DemoRequest) -> str:
    host = os.getenv("SMTP_HOST", "").strip()
    recipient = os.getenv("DEMO_REQUEST_EMAIL", "").strip()
    sender = os.getenv("SMTP_FROM", os.getenv("SMTP_USER", "")).strip()
    if not host or not recipient or not sender:
        return "not_configured"
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", recipient) or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", sender):
        logger.error("La dirección de origen o destino SMTP no tiene un formato válido")
        return "failed"

    message = EmailMessage()
    message["Subject"] = "Nueva solicitud de demostración — AURA Intelligence"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(
        "Se recibió una solicitud de demostración de AURA Intelligence.\n\n"
        f"Nombre: {demo.name}\n"
        f"Correo: {demo.email}\n"
        f"Empresa: {demo.company_name}\n"
        f"Cargo: {demo.job_title}\n"
        f"Sector: {demo.sector}\n"
        f"Tamaño: {demo.company_size or 'No indicado'}\n\n"
        f"Necesidad:\n{demo.need}\n\n"
        f"Mensaje:\n{demo.message or 'Sin mensaje adicional.'}\n"
        f"Solicitud registrada con ID {demo.id}."
    )

    try:
        port = int(os.getenv("SMTP_PORT", "587"))
        use_ssl = os.getenv("SMTP_USE_SSL", "false").strip().lower() in {"1", "true", "yes"}
        if use_ssl:
            smtp = smtplib.SMTP_SSL(host, port, timeout=10, context=ssl.create_default_context())
        else:
            smtp = smtplib.SMTP(host, port, timeout=10)
        with smtp:
            if not use_ssl and os.getenv("SMTP_STARTTLS", "true").strip().lower() in {"1", "true", "yes"}:
                smtp.starttls(context=ssl.create_default_context())
            username = os.getenv("SMTP_USER", "").strip()
            if username:
                smtp.login(username, os.getenv("SMTP_PASSWORD", ""))
            smtp.send_message(message)
        return "sent"
    except (OSError, smtplib.SMTPException, ValueError):
        logger.exception("No se pudo enviar la notificación de solicitud de demostración")
        return "failed"


@router.post("/", status_code=201)
def create_demo_request(
    payload: DemoRequestCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    _enforce_rate_limit(request)

    # Campo señuelo: descarta bots sin guardar la entrada ni revelar la detección.
    if payload.website:
        return {"accepted": True, "notification_status": "not_sent"}

    if not payload.consent:
        raise HTTPException(status_code=422, detail="Se requiere el consentimiento para tratar tus datos.")

    demo = DemoRequest(
        name=payload.name,
        email=payload.email.lower(),
        company_name=payload.company,
        job_title=payload.job_title,
        sector=payload.sector,
        company_size=payload.company_size or None,
        need=payload.need,
        message=payload.message or None,
        consent=True,
    )
    try:
        db.add(demo)
        db.commit()
        db.refresh(demo)
    except Exception:
        db.rollback()
        logger.exception("No se pudo guardar la solicitud de demostración")
        raise HTTPException(status_code=503, detail="No se pudo guardar la solicitud. Inténtalo de nuevo.")

    notification_status = _send_notification(demo)
    demo.notification_sent = notification_status == "sent"
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("No se pudo actualizar el estado de notificación de la solicitud")

    return {
        "accepted": True,
        "request_id": demo.id,
        "notification_status": notification_status,
    }


# ---- Consulta para administradores (correos en ADMIN_EMAILS del .env) ----
def _admin_emails() -> set[str]:
    return {e.strip().lower() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()}


def _is_admin(user: User) -> bool:
    return user.email.strip().lower() in _admin_emails()


@router.get("/is-admin")
def demo_is_admin(user: User = Depends(get_current_user)):
    return {"admin": _is_admin(user)}


@router.get("/")
def list_demo_requests(
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not _is_admin(user):
        raise HTTPException(status_code=403, detail="No tienes permiso para ver las solicitudes")
    rows = db.query(DemoRequest).order_by(DemoRequest.id.desc()).limit(max(1, min(limit, 500))).all()
    return [
        {
            "id": r.id, "created_at": r.created_at, "name": r.name, "email": r.email,
            "company_name": r.company_name, "job_title": r.job_title, "sector": r.sector,
            "company_size": r.company_size, "need": r.need, "message": r.message,
            "notification_sent": r.notification_sent,
        }
        for r in rows
    ]
