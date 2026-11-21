"""Importación masiva de clientes, productos y bodegas (carga inicial de pilotos).

El panel convierte el CSV en filas JSON. La importación es todo o nada: si una fila
falla, no se guarda ninguna y se devuelve la lista de errores por fila.
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session

from core.security import get_current_user
from database import get_db
from models import Customer, Event, Product, Relationship, User, Warehouse
from schemas import CustomerCreate, ProductCreate, WarehouseCreate

router = APIRouter(prefix="/import", tags=["Import"])

MAX_ROWS = 5000
MAX_ERRORS = 50

# entidad -> (esquema, modelo, campos, relación empresa -> entidad, etiqueta)
ENTITIES: dict[str, tuple[type[BaseModel], type, tuple[str, ...], str, str]] = {
    "customers": (CustomerCreate, Customer, ("name", "email", "phone"), "has_customer", "cliente"),
    "products": (ProductCreate, Product, ("sku", "name", "price"), "owns", "producto"),
    "warehouses": (WarehouseCreate, Warehouse, ("name", "location"), "operates", "bodega"),
}


class ImportRequest(BaseModel):
    rows: list[dict[str, Any]] = Field(min_length=1, max_length=MAX_ROWS)


def _clean(row: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    out = {}
    for key in fields:
        value = row.get(key)
        if isinstance(value, str):
            value = value.strip()
        if value not in (None, ""):
            out[key] = value
    return out


@router.post("/{entity}")
def import_rows(
    entity: str,
    body: ImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if entity not in ENTITIES:
        raise HTTPException(status_code=404, detail="Tipo de importación no soportado")
    schema, model, fields, rel_type, label = ENTITIES[entity]
    cid = current_user.company_id  # siempre la empresa del token

    errors: list[dict[str, Any]] = []
    valid: list[BaseModel] = []
    seen_skus: set[str] = set()
    existing_skus: set[str] = set()
    if entity == "products":
        existing_skus = {s for (s,) in db.query(Product.sku).filter(Product.company_id == cid)}

    for index, raw in enumerate(body.rows, start=1):
        data = _clean(raw, fields)
        if entity == "products" and isinstance(data.get("price"), str):
            data["price"] = data["price"].replace(" ", "").replace(",", ".")
        try:
            item = schema(company_id=cid, **data)
        except ValidationError as exc:
            msg = "; ".join(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors())
            errors.append({"row": index, "error": msg})
        else:
            if entity == "products":
                if item.sku in existing_skus:
                    errors.append({"row": index, "error": f"El SKU {item.sku} ya existe"})
                    continue
                if item.sku in seen_skus:
                    errors.append({"row": index, "error": f"SKU {item.sku} repetido en el archivo"})
                    continue
                seen_skus.add(item.sku)
            valid.append(item)
        if len(errors) >= MAX_ERRORS:
            break

    if errors:
        raise HTTPException(status_code=422, detail={"message": "No se importó ninguna fila", "errors": errors})

    try:
        records = [model(company_id=cid, **item.model_dump(exclude={"company_id"})) for item in valid]
        db.add_all(records)
        db.flush()
        db.add_all(
            Relationship(
                company_id=cid,
                source_type="company",
                source_id=cid,
                relationship_type=rel_type,
                target_type=entity[:-1],
                target_id=r.id,
            )
            for r in records
        )
        db.add(Event(
            company_id=cid,
            event_type=f"{entity[:-1]}.imported",
            entity_type=entity[:-1],
            description=f"Importación de {len(records)} registro(s) de {label}",
        ))
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {"imported": len(records)}
