from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from services.query_engine import query_company_summary
from core.security import get_current_user, require_company_access


router = APIRouter(
    prefix="/query",
    tags=["Query Engine"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/company/{company_id}")
def get_company_summary(
    company_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_company_access(company_id, current_user)
    result = query_company_summary(
        db,
        company_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada"
        )

    return result
