from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Company, Customer
from schemas import CustomerCreate

from services.relationships import create_relationship
from services.events import create_event
from core.security import get_current_user, require_company_access
from models import User


router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/")
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(customer.company_id, current_user)
    company = (
        db.query(Company)
        .filter(Company.id == customer.company_id)
        .first()
    )

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada"
        )

    new_customer = Customer(
        company_id=customer.company_id,
        name=customer.name,
        email=customer.email,
        phone=customer.phone
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    # Crear relación automática:
    # Company -> has_customer -> Customer
    create_relationship(
        db=db,
        company_id=company.id,
        source_type="company",
        source_id=company.id,
        relationship_type="has_customer",
        target_type="customer",
        target_id=new_customer.id
    )

    # Crear evento automático
    create_event(
        db=db,
        company_id=company.id,
        event_type="customer.created",
        entity_type="customer",
        entity_id=new_customer.id,
        description=f"Customer '{new_customer.name}' created"
    )

    return new_customer


@router.get("/")
def get_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Customer).filter(Customer.company_id == current_user.company_id).all()


@router.get("/{customer_id}")
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id, Customer.company_id == current_user.company_id)
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    return customer
