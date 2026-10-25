from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Relationship
from services.relationships import (
    create_relationship,
    get_entity_relationships
)
from core.security import get_current_user, require_company_access
from models import User
router = APIRouter(
    prefix="/relationships",
    tags=["Relationships"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/")
def add_relationship(
    company_id: int,
    source_type: str,
    source_id: int,
    relationship_type: str,
    target_type: str,
    target_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(company_id, current_user)
    relationship = create_relationship(
        db=db,
        company_id=company_id,
        source_type=source_type,
        source_id=source_id,
        relationship_type=relationship_type,
        target_type=target_type,
        target_id=target_id
    )

    return relationship


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
        raise HTTPException(
            status_code=404,
            detail="Relación no encontrada"
        )

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
