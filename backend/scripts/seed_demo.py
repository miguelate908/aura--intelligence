"""Crea (o recrea) una empresa ficticia con datos realistas para demostraciones de venta.

Uso, desde la carpeta backend:
    python scripts/seed_demo.py                 # correo demo@aura.local
    python scripts/seed_demo.py --email otra@aura.local

La contraseña se genera al azar y se imprime en la terminal; no se guarda en ningún archivo.
Todos los nombres son ficticios. Si ya existe un usuario con ese correo, se borran
su empresa y sus datos y se vuelven a crear.
"""
import argparse
import random
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import Base, SessionLocal, engine  # noqa: E402
from models import Company, Customer, Event, Product, Relationship, User, Warehouse  # noqa: E402
from routers.auth import pwd_context  # noqa: E402

COMPANY = "Distribuidora Andina Demo"
CUSTOMERS = [
    "Ferretería El Progreso", "Supermercado La Esquina", "Droguería Santa Clara", "Minimercado San José",
    "Tienda Naturista Vida", "Papelería Central", "Almacén Los Pinos", "Panadería La Espiga",
    "Restaurante Sabor Criollo", "Hotel Mirador", "Colegio Nuevo Horizonte", "Clínica Veterinaria Huellas",
    "Cafetería Aroma", "Distribuciones Norte", "Comercializadora Delta", "Mercados del Valle",
    "Licorera La 80", "Autoservicio El Ahorro", "Frutería Tropical", "Cigarrería Don Pedro",
]
PRODUCTS = [
    ("ARR-500", "Arroz premium 500 g", 3200), ("ARR-5K", "Arroz premium 5 kg", 29500),
    ("ACE-1L", "Aceite vegetal 1 L", 11800), ("AZU-1K", "Azúcar blanca 1 kg", 4900),
    ("CAF-250", "Café molido 250 g", 12400), ("CAF-500", "Café molido 500 g", 23100),
    ("PAS-250", "Pasta spaghetti 250 g", 2600), ("SAL-1K", "Sal refinada 1 kg", 1900),
    ("FRI-500", "Fríjol rojo 500 g", 6800), ("LEN-500", "Lenteja 500 g", 4300),
    ("ATU-170", "Atún en agua 170 g", 6900), ("LEC-1L", "Leche entera 1 L", 4200),
    ("DET-1K", "Detergente en polvo 1 kg", 13900), ("JAB-3U", "Jabón de baño x3", 8700),
    ("PAP-12", "Papel higiénico x12", 21500), ("GAS-1.5", "Gaseosa 1,5 L", 5600),
    ("AGU-600", "Agua sin gas 600 ml", 1800), ("GAL-12", "Galletas surtidas x12", 9800),
    ("CHO-100", "Chocolate de mesa 100 g", 3900), ("HAR-1K", "Harina de trigo 1 kg", 3700),
]
WAREHOUSES = [
    ("Bodega Principal", "Zona industrial, Medellín"),
    ("Centro de distribución Norte", "Bello, Antioquia"),
    ("Bodega Sur", "Itagüí, Antioquia"),
]


def wipe_company(db, company_id: int) -> None:
    for model in (Relationship, Event, Customer, Product, Warehouse, User):
        db.query(model).filter(model.company_id == company_id).delete(synchronize_session=False)
    db.query(Company).filter(Company.id == company_id).delete(synchronize_session=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--email", default="demo@aura.local")
    args = parser.parse_args()
    email = args.email.strip().lower()

    Base.metadata.create_all(bind=engine)
    rng = random.Random(7)
    password = secrets.token_urlsafe(12)

    with SessionLocal() as db:
        old = db.query(User).filter(User.email == email).first()
        if old:
            wipe_company(db, old.company_id)
            db.commit()
            db.expunge_all()

        company = Company(name=COMPANY)
        db.add(company)
        db.flush()
        cid = company.id
        db.add(User(company_id=cid, name="Usuario demo", email=email, password_hash=pwd_context.hash(password)))

        customers = [
            Customer(company_id=cid, name=n, email=f"compras{i + 1}@ejemplo.test", phone=f"300 555 {1000 + i:04d}")
            for i, n in enumerate(CUSTOMERS)
        ]
        products = [Product(company_id=cid, sku=s, name=n, price=p) for s, n, p in PRODUCTS]
        warehouses = [Warehouse(company_id=cid, name=n, location=loc) for n, loc in WAREHOUSES]
        db.add_all(customers + products + warehouses)
        db.flush()

        def rel(src_type, src_id, kind, tgt_type, tgt_id):
            db.add(Relationship(company_id=cid, source_type=src_type, source_id=src_id,
                                relationship_type=kind, target_type=tgt_type, target_id=tgt_id))

        for c in customers:
            rel("company", cid, "has_customer", "customer", c.id)
        for p in products:
            rel("company", cid, "owns", "product", p.id)
        for w in warehouses:
            rel("company", cid, "operates", "warehouse", w.id)
        for c in customers:
            for p in rng.sample(products, 3):
                rel("customer", c.id, "buys", "product", p.id)
        for p in products:
            rel("warehouse", rng.choice(warehouses).id, "stores", "product", p.id)

        for kind, items, label in (("customer", customers, "Customer"), ("product", products, "Product"),
                                   ("warehouse", warehouses, "Warehouse")):
            for it in items:
                db.add(Event(company_id=cid, event_type=f"{kind}.created", entity_type=kind,
                             entity_id=it.id, description=f"{label} '{it.name}' created"))
        db.commit()

    print(f"Empresa de demostración lista: {COMPANY}")
    print(f"  Correo:     {email}")
    print(f"  Contraseña: {password}")
    print(f"  {len(CUSTOMERS)} clientes, {len(PRODUCTS)} productos, {len(WAREHOUSES)} bodegas")


if __name__ == "__main__":
    main()
