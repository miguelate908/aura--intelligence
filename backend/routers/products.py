from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Company, Product
from schemas import ProductCreate, ProductUpdate

from services.relationships import create_relationship
from services.events import create_event
from services.records import delete_record, update_record
from core.security import get_current_user, require_company_access
from models import User


router = APIRouter(
    prefix="/products",
    tags=["Products"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/")
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(product.company_id, current_user)
    company = (
        db.query(Company)
        .filter(Company.id == product.company_id)
        .first()
    )

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada"
        )

    new_product = Product(
        company_id=product.company_id,
        sku=product.sku,
        name=product.name,
        price=product.price
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    # Crear relación automática:
    # Company -> owns -> Product
    create_relationship(
        db=db,
        company_id=company.id,
        source_type="company",
        source_id=company.id,
        relationship_type="owns",
        target_type="product",
        target_id=new_product.id
    )

    # Crear evento automático
    create_event(
        db=db,
        company_id=company.id,
        event_type="product.created",
        entity_type="product",
        entity_id=new_product.id,
        description=f"Product '{new_product.name}' created"
    )

    return new_product


@router.get("/")
def get_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Product).filter(Product.company_id == current_user.company_id).order_by(Product.id).all()


@router.get("/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.company_id == current_user.company_id)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    return product


@router.put("/{record_id}")
def update_product(
    record_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_record(db, Product, record_id, current_user.company_id, payload.model_dump(), "product", "Producto no encontrado")


@router.delete("/{record_id}", status_code=204)
def delete_product(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_record(db, Product, record_id, current_user.company_id, "product", "Producto no encontrado")
