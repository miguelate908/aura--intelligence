from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Company, Customer, Product, Relationship, User, Warehouse
from services.relationships import (
    create_relationship,
    get_entity_relationships,
)
from core.security import get_current_user, require_company_access

router = APIRouter(
    prefix="/relationships",
    tags=["Relationships"],
    dependencies=[Depends(get_current_user)],
)

# Tipos de entidad que el sistema sabe resolver (los mismos que usa el grafo).
ENTITY_MODELS = {"company": Company, "customer": Customer, "product": Product, "warehouse": Warehouse}
Text100 = Annotated[str, Query(min_length=1, max_length=100)]


def _entity_exists(db: Session, entity_type: str, entity_id: int, company_id: int) -> bool:
    model = ENTITY_MODELS.get(entity_type)
    if model is None:
        raise HTTPException(status_code=422, detail=f"Tipo de entidad no soportado: {entity_type}")
    if model is Company:
        return entity_id == company_id
    return (
        db.query(model.id)
        .filter(model.id == entity_id, model.company_id == company_id)
        .first()
        is not None
    )


@router.post("/")
def add_relationship(
    company_id: int,
    source_id: int,
    target_id: int,
    source_type: Text100,
    relationship_type: Text100,
    target_type: Text100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(company_id, current_user)
    # Origen y destino deben existir y pertenecer a la misma empresa.
    if not _entity_exists(db, source_type, source_id, company_id):
        raise HTTPException(status_code=404, detail="Entidad de origen no encontrada")
    if not _entity_exists(db, target_type, target_id, company_id):
        raise HTTPException(status_code=404, detail="Entidad de destino no encontrada")
    return create_relationship(
        db=db,
        company_id=company_id,
        source_type=source_type,
        source_id=source_id,
        relationship_type=relationship_type,
        target_type=target_type,
        target_id=target_id,
    )


@router.get("/")
def get_relationships(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Relationship).filter(Relationship.company_id == current_user.company_id).all()


@router.get("/{relationship_id}")
def get_relationship(
    relationship_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    relationship = (
        db.query(Relationship)
        .filter(Relationship.id == relationship_id, Relationship.company_id == current_user.company_id)
        .first()
    )
    if relationship is None:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    return relationship


@router.get("/entity/{entity_type}/{entity_id}")
def get_entity_graph(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_entity_relationships(
        db=db,
        entity_type=entity_type,
        entity_id=entity_id,
        company_id=current_user.company_id,
    )
