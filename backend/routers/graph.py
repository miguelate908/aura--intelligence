from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from services.graph import get_graph
from core.security import get_current_user


router = APIRouter(
    prefix="/graph",
    tags=["Graph"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/entity/{entity_type}/{entity_id}")
def get_entity_graph(
    entity_type: str,
    entity_id: int,
    depth: int = Query(default=1, ge=1, le=3),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_graph(
        db=db,
        entity_type=entity_type,
        entity_id=entity_id,
        depth=depth,
        company_id=current_user.company_id,
    )
