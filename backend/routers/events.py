from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Event
from models import User
from core.security import get_current_user, require_company_access


router = APIRouter(
    prefix="/events",
    tags=["Events"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/")
def get_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Event)
        .filter(Event.company_id == current_user.company_id)
        .order_by(Event.created_at.desc())
        .all()
    )


@router.get("/{event_id}")
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = (
        db.query(Event)
        .filter(Event.id == event_id, Event.company_id == current_user.company_id)
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Evento no encontrado"
        )

    return event


@router.get("/company/{company_id}")
def get_company_events(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(company_id, current_user)
    return (
        db.query(Event)
        .filter(Event.company_id == company_id)
        .order_by(Event.created_at.desc())
        .all()
    )
