import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database import engine, Base, SessionLocal
import models
from routers import auth, assistant, companies, customers, products, warehouses, events, relationships, graph, contact
# `query`: súmalo si expone `router`.

Base.metadata.create_all(bind=engine)

CONTACT_RETENTION_DAYS = 7  # debe coincidir con la política de privacidad y con la página Contactos


def purge_old_contacts() -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=CONTACT_RETENTION_DAYS)
    with SessionLocal() as db:
        db.query(models.ContactRequest).filter(models.ContactRequest.created_at < cutoff).delete(synchronize_session=False)
        db.commit()


async def _purge_loop() -> None:
    while True:
        try:
            await asyncio.to_thread(purge_old_contacts)
        except Exception:
            logging.exception("No se pudo purgar contactos antiguos")
        await asyncio.sleep(3600)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    task = asyncio.create_task(_purge_loop())
    yield
    task.cancel()


PROD = os.getenv("APP_ENV") == "production"
app = FastAPI(
    lifespan=lifespan,
    title="AURA Intelligence API",
    version="0.1.0",
    docs_url=None if PROD else "/docs",      # en producción no se publica la documentación
    redoc_url=None,
    openapi_url=None if PROD else "/openapi.json",
)

for r in (auth, assistant, companies, customers, products, warehouses, events, relationships, graph, contact):
    app.include_router(r.router)


@app.middleware("http")
async def strip_api_prefix_and_harden(request: Request, call_next):
    # El frontend llama a /api/...; Vite quita ese prefijo en desarrollo y aquí se quita en producción.
    path = request.scope["path"]
    if path == "/api" or path.startswith("/api/"):
        request.scope["path"] = path[4:] or "/"
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    return response


@app.get("/health")
def health():
    return {"status": "ok"}


# Si existe frontend/dist (tras `npm run build`), FastAPI también sirve el sitio.
DIST = (Path(__file__).resolve().parent.parent / "frontend" / "dist").resolve()
if (DIST / "index.html").is_file():
    if (DIST / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        candidate = (DIST / full_path).resolve()
        if full_path and candidate.is_file() and DIST in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(DIST / "index.html")  # rutas de React: /login, /app, /privacidad...
else:
    @app.get("/")
    def root():
        return {"message": "AURA Intelligence API funcionando"}
