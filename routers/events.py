from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Company, Event
from schemas import EventCreate


router = APIRouter(
    prefix="/events",
    tags=["Events"]
)


@router.post("/")
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db)
):
    company = (
        db.query(Company)
        .filter(Company.id == event.company_id)
        .first()
    )

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada"
        )

    new_event = Event(
        company_id=event.company_id,
        event_type=event.event_type,
        entity_type=event.entity_type,
        entity_id=event.entity_id,
        description=event.description
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event


@router.get("/")
def get_events(
    db: Session = Depends(get_db)
):
    return (
        db.query(Event)
        .order_by(Event.created_at.desc())
        .all()
    )


@router.get("/{event_id}")
def get_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    event = (
        db.query(Event)
        .filter(Event.id == event_id)
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Evento no encontrado"
        )

    return event