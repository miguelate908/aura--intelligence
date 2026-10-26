from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Company, User
from core.security import get_current_user

# Nota: se eliminó POST /companies/. Era público (sin autenticación ni límite) y las
# empresas se crean desde /auth/register, que sí tiene límite de intentos.
router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/")
def get_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Company).filter(Company.id == current_user.company_id).all()


@router.get("/{company_id}")
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company = (
        db.query(Company)
        .filter(Company.id == company_id, Company.id == current_user.company_id)
        .first()
    )
    if company is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return company
