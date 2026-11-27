"""Resumen del panel: conteos y actividad reciente de la empresa con sesión iniciada.

Sustituye las cuatro descargas completas que hacía el panel solo para contar filas.
Los conteos se hacen con COUNT en la base y la actividad se limita a los últimos eventos.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.security import get_current_user
from database import get_db
from models import Customer, Event, Product, User, Warehouse

RECENT_EVENTS = 5

router = APIRouter(prefix="/summary", tags=["Summary"])


@router.get("/")
def get_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cid = current_user.company_id

    def count(model) -> int:
        return db.query(func.count(model.id)).filter(model.company_id == cid).scalar() or 0

    recent = (
        db.query(Event)
        .filter(Event.company_id == cid)
        .order_by(Event.created_at.desc(), Event.id.desc())
        .limit(RECENT_EVENTS)
        .all()
    )
    return {
        "counts": {
            "customers": count(Customer),
            "products": count(Product),
            "warehouses": count(Warehouse),
            "events": count(Event),
        },
        "recent_events": [
            {"event_type": e.event_type, "description": e.description, "created_at": e.created_at}
            for e in recent
        ],
    }
