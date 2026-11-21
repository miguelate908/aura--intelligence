"""Captación de clientes potenciales: formulario público de la página comercial."""
import logging
import os
import secrets
import smtplib
import threading
import time
from email.message import EmailMessage
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import Session

from database import Base, get_db

logger = logging.getLogger("aura.contact")
router = APIRouter(prefix="/contact", tags=["Contact"])

MAX_PER_HOUR = 5  # solicitudes por IP
_hits: dict[str, list[float]] = {}
_lock = threading.Lock()


class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, index=True)
    company = Column(String(150), nullable=False)
    job_title = Column(String(150), nullable=False)
    sector = Column(String(50), nullable=False)
    company_size = Column(String(30), nullable=True)
    need = Column(String(1000), nullable=False)
    message = Column(String(2000), nullable=True)
    ip = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ContactIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    full_name: str = Field(min_length=2, max_length=150)
    email: str = Field(pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$", max_length=150)
    company: str = Field(min_length=1, max_length=150)
    job_title: str = Field(min_length=1, max_length=150)
    sector: str = Field(min_length=1, max_length=50)
    company_size: Optional[str] = Field(default=None, max_length=30)
    need: str = Field(min_length=10, max_length=1000)
    message: Optional[str] = Field(default=None, max_length=2000)
    consent: bool = False
    website: Optional[str] = None  # campo trampa: los humanos lo dejan vacío


def _allowed(ip: str) -> bool:
    now = time.time()
    with _lock:
        recent = [t for t in _hits.get(ip, []) if now - t < 3600]
        ok = len(recent) < MAX_PER_HOUR
        if ok:
            recent.append(now)
        _hits[ip] = recent
        return ok


def _clean(v) -> str:
    return " ".join(str(v or "").split())[:300]


def notify_new_lead(data: dict) -> None:
    """Avisa por correo de un contacto nuevo. Solo actúa si SMTP_HOST y LEADS_NOTIFY_TO están configurados."""
    host, to = os.getenv("SMTP_HOST"), os.getenv("LEADS_NOTIFY_TO")
    if not host or not to:
        return
    try:
        user, pwd = os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD")
        msg = EmailMessage()
        msg["Subject"] = f"Nuevo contacto en EDITH: {_clean(data['company'])}"
        msg["From"] = os.getenv("SMTP_FROM") or user or to
        msg["To"] = to
        msg["Reply-To"] = _clean(data["email"])
        msg.set_content(
            "Nuevo contacto desde la página comercial\n\n"
            + "\n".join(f"{k}: {data.get(k) or '-'}" for k in
                         ("full_name", "email", "company", "job_title", "sector", "company_size", "need", "message"))
        )
        with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587")), timeout=15) as smtp:
            smtp.starttls()
            if user and pwd:
                smtp.login(user, pwd)
            smtp.send_message(msg)
    except Exception:
        logger.exception("No se pudo enviar el aviso de contacto (el contacto sí quedó guardado)")


@router.post("", status_code=201)
def create_lead(body: ContactIn, request: Request, tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if body.website:  # bot: responde "ok" sin guardar nada
        return {"ok": True}
    if not body.consent:
        raise HTTPException(status_code=422, detail="Debes aceptar el tratamiento de datos personales")
    ip = request.client.host if request.client else "desconocida"
    if not _allowed(ip):
        raise HTTPException(status_code=429, detail="Demasiados intentos. Inténtalo más tarde.")
    data = body.model_dump(exclude={"consent", "website"})
    db.add(Lead(ip=ip, **data))
    db.commit()
    tasks.add_task(notify_new_lead, data)
    return {"ok": True}


@router.get("/leads")
def list_leads(x_admin_key: Optional[str] = Header(default=None), db: Session = Depends(get_db)):
    """Solo para el dueño del sitio: requiere ADMIN_API_KEY en el .env y el encabezado X-Admin-Key."""
    key = os.getenv("ADMIN_API_KEY")
    if not key:
        raise HTTPException(status_code=404, detail="No encontrado")
    if not x_admin_key or not secrets.compare_digest(x_admin_key, key):
        raise HTTPException(status_code=403, detail="Acceso denegado")
    rows = db.query(Lead).order_by(Lead.id.desc()).limit(200).all()
    return [
        {c.name: (v.isoformat() if hasattr(v, "isoformat") else v) for c in Lead.__table__.columns for v in [getattr(r, c.name)]}
        for r in rows
    ]
