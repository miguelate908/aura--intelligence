import re
import unicodedata
 
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session
 
from core.security import get_current_user
from database import get_db
from models import Company, Customer, Event, Product, User, Warehouse
 
router = APIRouter(prefix="/assistant", tags=["Assistant"])
 
MAX_ITEMS = 10
 
 
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
 
 
class ChatResponse(BaseModel):
    reply: str
    intent: str
 
 
def _norm(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")
 
 
def _has(text: str, *words: str) -> bool:
    return any(w in text for w in words)
 
 
def _money(value) -> str:
    return f"{(value or 0):,.2f}"
 
 
def _lines(items) -> str:
    return "\n".join(f"- {i}" for i in items)
 
 
def _count(db: Session, model, cid: int) -> int:
    return db.query(func.count(model.id)).filter(model.company_id == cid).scalar() or 0
 
 
def _summary(db: Session, cid: int) -> str:
    company = db.query(Company).filter(Company.id == cid).first()
    name = company.name if company else "tu empresa"
    return (
        f"Resumen de {name}:\n"
        f"- Clientes: {_count(db, Customer, cid)}\n"
        f"- Productos: {_count(db, Product, cid)}\n"
        f"- Bodegas: {_count(db, Warehouse, cid)}\n"
        f"- Eventos registrados: {_count(db, Event, cid)}"
    )
 
 
def _customers(db: Session, cid: int, t: str) -> str:
    total = _count(db, Customer, cid)
    if total == 0:
        return "Todavía no tienes clientes registrados."
    if _has(t, "cuantos", "cuantas", "total", "numero"):
        return f"Tienes {total} cliente(s) registrado(s)."
    rows = db.query(Customer).filter(Customer.company_id == cid).order_by(Customer.id.desc()).limit(MAX_ITEMS).all()
    extra = f"\n(Mostrando {len(rows)} de {total})" if total > len(rows) else ""
    return "Tus clientes más recientes:\n" + _lines(
        f"{c.name}" + (f" · {c.email}" if c.email else "") for c in rows
    ) + extra
 
 
def _products(db: Session, cid: int, t: str) -> str:
    q = db.query(Product).filter(Product.company_id == cid)
    total = q.count()
    if total == 0:
        return "Todavía no tienes productos registrados."
    if _has(t, "cuantos", "cuantas", "total", "numero"):
        return f"Tienes {total} producto(s) registrado(s)."
    num = re.search(r"\d+(?:[.,]\d+)?", t)
    if num:
        limit = float(num.group().replace(",", "."))
        if _has(t, "mayor", "mas de", "superior", "arriba"):
            q = q.filter(Product.price > limit)
            title = f"Productos con precio mayor a {_money(limit)}:"
        elif _has(t, "menor", "menos de", "inferior", "debajo", "barato"):
            q = q.filter(Product.price < limit)
            title = f"Productos con precio menor a {_money(limit)}:"
        else:
            q, title = q.order_by(Product.id.desc()), "Tus productos:"
    elif _has(t, "mas caro", "mas costoso"):
        q, title = q.order_by(Product.price.desc()), "Tus productos más caros:"
    elif _has(t, "mas barato", "mas economico"):
        q, title = q.order_by(Product.price.asc()), "Tus productos más económicos:"
    else:
        q, title = q.order_by(Product.id.desc()), "Tus productos más recientes:"
    rows = q.limit(MAX_ITEMS).all()
    if not rows:
        return "No encontré productos con ese criterio."
    return title + "\n" + _lines(f"{p.name} (SKU {p.sku}) · {_money(p.price)}" for p in rows)
 
 
def _warehouses(db: Session, cid: int, t: str) -> str:
    rows = db.query(Warehouse).filter(Warehouse.company_id == cid).limit(MAX_ITEMS).all()
    if not rows:
        return "Todavía no tienes bodegas registradas."
    if _has(t, "cuantos", "cuantas", "total", "numero"):
        return f"Tienes {_count(db, Warehouse, cid)} bodega(s)."
    return "Tus bodegas:\n" + _lines(f"{w.name}" + (f" · {w.location}" if w.location else "") for w in rows)
 
 
def _events(db: Session, cid: int) -> str:
    rows = db.query(Event).filter(Event.company_id == cid).order_by(Event.id.desc()).limit(5).all()
    if not rows:
        return "Todavía no hay actividad registrada."
    return "Actividad reciente:\n" + _lines(f"{e.event_type}: {e.description or 'sin descripción'}" for e in rows)
 
 
def _search(db: Session, cid: int, raw: str) -> str:
    term = re.sub(r"^\s*(busca|buscar|encuentra|encontrar)\s+", "", raw, flags=re.I).strip()
    if len(term) < 2:
        return "¿Qué quieres buscar? Escribe, por ejemplo: busca Juan."
    like = f"%{term}%"
    cust = db.query(Customer).filter(Customer.company_id == cid, Customer.name.ilike(like)).limit(5).all()
    prod = db.query(Product).filter(Product.company_id == cid, Product.name.ilike(like)).limit(5).all()
    if not cust and not prod:
        return f"No encontré resultados para «{term}»."
    out = []
    if cust:
        out.append("Clientes:\n" + _lines(c.name for c in cust))
    if prod:
        out.append("Productos:\n" + _lines(f"{p.name} · {_money(p.price)}" for p in prod))
    return "\n\n".join(out)
 
 
def _dupes(db: Session, column, cid: int, model) -> list:
    """Valores repetidos (sin distinguir mayúsculas ni espacios) dentro de la empresa."""
    key = func.lower(func.trim(column))
    return (
        db.query(key, func.count(model.id))
        .filter(model.company_id == cid, column.isnot(None), func.trim(column) != "")
        .group_by(key)
        .having(func.count(model.id) > 1)
        .order_by(func.count(model.id).desc(), key)
        .limit(5)
        .all()
    )


def _quality(db: Session, cid: int) -> str:
    customers = _count(db, Customer, cid)
    products = _count(db, Product, cid)
    if customers == 0 and products == 0:
        return "Todavía no hay datos que revisar. Importa clientes o productos primero."
    findings = []
    if customers:
        no_contact = (
            db.query(func.count(Customer.id))
            .filter(
                Customer.company_id == cid,
                func.coalesce(func.trim(Customer.email), "") == "",
                func.coalesce(func.trim(Customer.phone), "") == "",
            )
            .scalar() or 0
        )
        if no_contact:
            findings.append(f"{no_contact} de {customers} cliente(s) sin correo ni teléfono: no se pueden contactar.")
        for email, n in _dupes(db, Customer.email, cid, Customer):
            findings.append(f"Correo repetido en {n} clientes: {email}")
        for name, n in _dupes(db, Customer.name, cid, Customer):
            findings.append(f"Nombre de cliente repetido {n} veces: {name}")
    if products:
        zero = (
            db.query(func.count(Product.id))
            .filter(Product.company_id == cid, func.coalesce(Product.price, 0) <= 0)
            .scalar() or 0
        )
        if zero:
            findings.append(f"{zero} de {products} producto(s) con precio 0 o sin precio.")
        for sku, n in _dupes(db, Product.sku, cid, Product):
            findings.append(f"SKU repetido en {n} productos: {sku}")
    header = f"Revisión de calidad de datos ({customers} cliente(s), {products} producto(s)):"
    if not findings:
        return header + "\nNo encontré problemas: sin duplicados, sin precios en 0 y todos los clientes tienen un dato de contacto."
    return header + "\n" + _lines(findings) + "\n\nCorrígelos en Clientes o Productos, o vuelve a importar el CSV corregido."


HELP = (
    "Puedo ayudarte con información de tu empresa. Prueba con:\n"
    "- «Resumen de mi empresa»\n"
    "- «¿Cuántos clientes tengo?»\n"
    "- «Productos con precio mayor a 100»\n"
    "- «¿Qué bodegas tengo?»\n"
    "- «Actividad reciente»\n"
    "- «Revisa la calidad de mis datos»\n"
    "- «Busca <nombre>»"
)
 
 
@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cid = current_user.company_id  # siempre la empresa del token: nunca se acepta otra
    raw = body.message.strip()
    t = _norm(raw)
 
    if _has(t, "ayuda", "que puedes", "que sabes", "como funciona") or t in ("hola", "buenas", "hey"):
        intent, reply = "help", HELP
    elif t.startswith(("busca", "buscar", "encuentra")):
        intent, reply = "search", _search(db, cid, raw)
    elif _has(t, "resumen", "general", "panorama", "estado de mi empresa"):
        intent, reply = "summary", _summary(db, cid)
    elif _has(t, "calidad", "duplicad", "repetid", "incomplet", "revisa mis datos", "revisa los datos"):
        intent, reply = "quality", _quality(db, cid)
    elif _has(t, "evento", "actividad", "historial") or (
        _has(t, "reciente") and not _has(t, "cliente", "producto", "bodega", "almacen")
    ):
        intent, reply = "events", _events(db, cid)
    elif _has(t, "cliente"):
        intent, reply = "customers", _customers(db, cid, t)
    elif _has(t, "producto", "precio", "sku", "articulo"):
        intent, reply = "products", _products(db, cid, t)
    elif _has(t, "bodega", "almacen", "inventario"):
        intent, reply = "warehouses", _warehouses(db, cid, t)
    else:
        intent = "fallback"
        reply = "No tengo información para responder eso con seguridad.\n\n" + HELP

    return ChatResponse(reply=reply, intent=intent)
