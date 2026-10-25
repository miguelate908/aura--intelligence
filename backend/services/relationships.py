from sqlalchemy.orm import Session

from models import Relationship


def create_relationship(
    db: Session,
    company_id: int,
    source_type: str,
    source_id: int,
    relationship_type: str,
    target_type: str,
    target_id: int
):
    existing_relationship = (
        db.query(Relationship)
        .filter(
            Relationship.company_id == company_id,
            Relationship.source_type == source_type,
            Relationship.source_id == source_id,
            Relationship.relationship_type == relationship_type,
            Relationship.target_type == target_type,
            Relationship.target_id == target_id
        )
        .first()
    )

    if existing_relationship:
        return existing_relationship

    relationship = Relationship(
        company_id=company_id,
        source_type=source_type,
        source_id=source_id,
        relationship_type=relationship_type,
        target_type=target_type,
        target_id=target_id
    )

    db.add(relationship)
    db.commit()
    db.refresh(relationship)

    return relationship


def get_entity_relationships(
    db: Session,
    entity_type: str,
    entity_id: int,
    company_id: int,
):
    return (
        db.query(Relationship)
        .filter(
            Relationship.company_id == company_id,
            (
                (Relationship.source_type == entity_type)
                & (Relationship.source_id == entity_id)
            )
            |
            (
                (Relationship.target_type == entity_type)
                & (Relationship.target_id == entity_id)
            )
        )
        .all()
    )
