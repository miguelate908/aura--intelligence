"""Crea la empresa y el usuario administrador de un cliente (piloto o plan pagado).

Uso, desde la carpeta backend (con DATABASE_URL apuntando a la base de producción):
    python scripts/create_client.py --company "Distribuidora XYZ" --name "Ana Pérez" --email ana@xyz.com

Genera una contraseña temporal aleatoria y la imprime una sola vez. Envíasela al cliente
por un canal distinto al del correo de bienvenida y pídele que la guarde en un lugar seguro.
"""
import argparse
import re
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import func  # noqa: E402

from database import Base, SessionLocal, engine  # noqa: E402
from models import Company, User  # noqa: E402
from routers.auth import pwd_context  # noqa: E402

EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--company", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--email", required=True)
    args = parser.parse_args()

    company_name, name, email = args.company.strip(), args.name.strip(), args.email.strip().lower()
    if not company_name or not name or len(company_name) > 150 or len(name) > 150:
        sys.exit("Empresa y nombre son obligatorios (máximo 150 caracteres).")
    if not EMAIL.match(email) or len(email) > 150:
        sys.exit("Correo no válido.")

    Base.metadata.create_all(bind=engine)
    password = secrets.token_urlsafe(12)  # 16 caracteres
    with SessionLocal() as db:
        if db.query(User).filter(func.lower(User.email) == email).first():
            sys.exit(f"Ya existe un usuario con el correo {email}.")
        company = Company(name=company_name)
        db.add(company)
        db.flush()
        db.add(User(company_id=company.id, name=name, email=email, password_hash=pwd_context.hash(password)))
        db.commit()
        company_id = company.id

    print(f"Cliente creado: {company_name} (empresa #{company_id})")
    print(f"  Correo:               {email}")
    print(f"  Contraseña temporal:  {password}")


if __name__ == "__main__":
    main()
