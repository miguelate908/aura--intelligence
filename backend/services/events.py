from sqlalchemy.orm import Session

from models import Event


def create_event(
    db: Session,
    company_id: int,
    event_type: str,
    entity_type: str | None = None,
    entity_id: int | None = None,
    description: str | None = None,
):
    event = Event(
        company_id=company_id,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event