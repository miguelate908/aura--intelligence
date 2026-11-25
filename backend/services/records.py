"""Edición y eliminación de registros de una empresa (clientes, productos, bodegas).

Siempre filtra por company_id del usuario: un registro de otra empresa responde 404,
igual que si no existiera. Al eliminar se borran también sus relaciones del grafo;
los eventos se conservan como historial y se registra uno nuevo de eliminación.
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Relationship
from services.events import create_event


def _get_owned(db: Session, model, record_id: int, company_id: int, not_found: str):
    record = db.query(model).filter(model.id == record_id, model.company_id == company_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail=not_found)
    return record


def update_record(db: Session, model, record_id: int, company_id: int, data: dict, entity_type: str, not_found: str):
    record = _get_owned(db, model, record_id, company_id, not_found)
    for field, value in data.items():
        setattr(record, field, value)
    # create_event confirma en una sola transacción el registro y su evento.
    create_event(
        db=db,
        company_id=company_id,
        event_type=f"{entity_type}.updated",
        entity_type=entity_type,
        entity_id=record.id,
        description=f"{entity_type.capitalize()} '{record.name}' updated",
    )
    return record


def delete_record(db: Session, model, record_id: int, company_id: int, entity_type: str, not_found: str) -> None:
    record = _get_owned(db, model, record_id, company_id, not_found)
    name = record.name
    db.query(Relationship).filter(
        Relationship.company_id == company_id,
        (
            ((Relationship.source_type == entity_type) & (Relationship.source_id == record_id))
            | ((Relationship.target_type == entity_type) & (Relationship.target_id == record_id))
        ),
    ).delete(synchronize_session=False)
    db.delete(record)
    # Las relaciones, el registro y el evento comparten el mismo commit.
    create_event(
        db=db,
        company_id=company_id,
        event_type=f"{entity_type}.deleted",
        entity_type=entity_type,
        entity_id=record_id,
        description=f"{entity_type.capitalize()} '{name}' deleted",
    )
