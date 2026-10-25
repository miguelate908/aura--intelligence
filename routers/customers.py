from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Company, Customer
from schemas import CustomerCreate


router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


@router.post("/")
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
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

    return new_customer


@router.get("/")
def get_customers(
    db: Session = Depends(get_db)
):
    return db.query(Customer).all()


@router.get("/{customer_id}")
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    return customer