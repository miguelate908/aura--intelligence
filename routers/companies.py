from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Company
from schemas import CompanyCreate
from services.events import create_event


router = APIRouter(
    prefix="/companies",
    tags=["Companies"]
)


@router.post("/")
def create_company(
    company: CompanyCreate,
    db: Session = Depends(get_db)
):
    new_company = Company(
        name=company.name
    )

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    create_event(
        db=db,
        company_id=new_company.id,
        event_type="company.created",
        entity_type="company",
        entity_id=new_company.id,
        description=f"Company '{new_company.name}' created"
    )

    db.commit()

    return new_company


@router.get("/")
def get_companies(
    db: Session = Depends(get_db)
):
    return db.query(Company).all()


@router.get("/{company_id}")
def get_company(
    company_id: int,
    db: Session = Depends(get_db)
):
    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada"
        )

    return company