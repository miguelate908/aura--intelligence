"""Migración mínima e idempotente: añade columnas nuevas a demo_requests si faltan.
create_all() crea tablas nuevas pero no agrega columnas a tablas que ya existen.
Cuando el proyecto crezca, conviene pasar a Alembic."""
from sqlalchemy import text

_STATEMENTS = [
    "ALTER TABLE demo_requests ADD COLUMN IF NOT EXISTS job_title VARCHAR(150)",
    "ALTER TABLE demo_requests ADD COLUMN IF NOT EXISTS sector VARCHAR(50)",
    "ALTER TABLE demo_requests ADD COLUMN IF NOT EXISTS company_size VARCHAR(50)",
    "ALTER TABLE demo_requests ADD COLUMN IF NOT EXISTS need TEXT",
    "ALTER TABLE demo_requests ADD COLUMN IF NOT EXISTS consent BOOLEAN NOT NULL DEFAULT FALSE",
]


def ensure_demo_request_columns(engine) -> None:
    if engine.dialect.name != "postgresql":
        return  # ADD COLUMN IF NOT EXISTS es de PostgreSQL; en SQLite (pruebas) create_all ya crea la tabla completa
    with engine.begin() as conn:
        for stmt in _STATEMENTS:
            conn.execute(text(stmt))
