from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Company, Warehouse
from schemas import WarehouseCreate

from services.relationships import create_relationship
from services.events import create_event
from core.security import get_current_user, require_company_access
from models import User


router = APIRouter(
    prefix="/warehouses",
    tags=["Warehouses"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/")
def create_warehouse(
    warehouse: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(warehouse.company_id, current_user)
    company = (
        db.query(Company)
        .filter(Company.id == warehouse.company_id)
        .first()
    )

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada"
        )

    new_warehouse = Warehouse(
        company_id=warehouse.company_id,
        name=warehouse.name,
        location=warehouse.location
    )

    db.add(new_warehouse)
    db.commit()
    db.refresh(new_warehouse)

    # Crear relación automática:
    # Company -> operates -> Warehouse
    create_relationship(
        db=db,
        company_id=company.id,
        source_type="company",
        source_id=company.id,
        relationship_type="operates",
        target_type="warehouse",
        target_id=new_warehouse.id
    )

    # Crear evento automático
    create_event(
        db=db,
        company_id=company.id,
        event_type="warehouse.created",
        entity_type="warehouse",
        entity_id=new_warehouse.id,
        description=f"Warehouse '{new_warehouse.name}' created"
    )

    return new_warehouse


@router.get("/")
def get_warehouses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Warehouse).filter(Warehouse.company_id == current_user.company_id).all()
