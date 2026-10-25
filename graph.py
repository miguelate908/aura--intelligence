from sqlalchemy.orm import Session

from models import (
    Relationship,
    Company,
    Product,
    Customer,
    Warehouse
)


def get_entity_data(db: Session, entity_type: str, entity_id: int, company_id: int):

    if entity_type == "company":
        entity = (
            db.query(Company)
            .filter(Company.id == entity_id, Company.id == company_id)
            .first()
        )

        if entity is None:
            return None

        return {
            "type": "company",
            "id": entity.id,
            "name": entity.name,
            "created_at": entity.created_at
        }

    elif entity_type == "product":
        entity = (
            db.query(Product)
            .filter(Product.id == entity_id, Product.company_id == company_id)
            .first()
        )

        if entity is None:
            return None

        return {
            "type": "product",
            "id": entity.id,
            "company_id": entity.company_id,
            "sku": entity.sku,
            "name": entity.name,
            "price": entity.price
        }

    elif entity_type == "customer":
        entity = (
            db.query(Customer)
            .filter(Customer.id == entity_id, Customer.company_id == company_id)
            .first()
        )

        if entity is None:
            return None

        return {
            "type": "customer",
            "id": entity.id,
            "company_id": entity.company_id,
            "name": entity.name,
            "email": entity.email,
            "phone": entity.phone
        }

    elif entity_type == "warehouse":
        entity = (
            db.query(Warehouse)
            .filter(Warehouse.id == entity_id, Warehouse.company_id == company_id)
            .first()
        )

        if entity is None:
            return None

        return {
            "type": "warehouse",
            "id": entity.id,
            "company_id": entity.company_id,
            "name": entity.name,
            "location": entity.location
        }

    return None


def get_graph(
    db: Session,
    entity_type: str,
    entity_id: int,
    company_id: int,
    depth: int = 1,
):

    visited_entities = set()
    visited_relationships = set()
    added_nodes = set()

    nodes = []
    relationships = []

    def add_node(node_type: str, node_id: int):

        key = (node_type, node_id)

        if key in visited_entities or key in added_nodes:
            return

        entity_data = get_entity_data(
            db,
            node_type,
            node_id,
            company_id,
        )

        if entity_data is not None:
            nodes.append(entity_data)
            added_nodes.add(key)

    def explore(
        current_type: str,
        current_id: int,
        current_depth: int
    ):

        if current_depth > depth:
            return

        entity_key = (
            current_type,
            current_id
        )

        if entity_key in visited_entities:
            return

        add_node(
            current_type,
            current_id
        )

        visited_entities.add(entity_key)

        found_relationships = (
            db.query(Relationship)
            .filter(
                Relationship.company_id == company_id,
                (
                    (Relationship.source_type == current_type)
                    &
                    (Relationship.source_id == current_id)
                )
                |
                (
                    (Relationship.target_type == current_type)
                    &
                    (Relationship.target_id == current_id)
                )
            )
            .all()
        )

        for relationship in found_relationships:

            if relationship.id in visited_relationships:
                continue

            visited_relationships.add(
                relationship.id
            )

            relationships.append({
                "id": relationship.id,
                "source": {
                    "type": relationship.source_type,
                    "id": relationship.source_id
                },
                "relationship": relationship.relationship_type,
                "target": {
                    "type": relationship.target_type,
                    "id": relationship.target_id
                }
            })

            if (
                relationship.source_type == current_type
                and relationship.source_id == current_id
            ):
                next_type = relationship.target_type
                next_id = relationship.target_id

            else:
                next_type = relationship.source_type
                next_id = relationship.source_id

            if current_depth < depth:
                explore(
                    next_type,
                    next_id,
                    current_depth + 1
                )
            else:
                add_node(
                    next_type,
                    next_id
                )

    explore(
        entity_type,
        entity_id,
        1
    )

    return {
        "entity": {
            "type": entity_type,
            "id": entity_id
        },
        "nodes": nodes,
        "relationships": relationships
    }
