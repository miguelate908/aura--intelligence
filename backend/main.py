import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from database import engine, Base, SessionLocal
from core.migrations import ensure_demo_request_columns
from core.security import get_current_user
from models import DemoRequest

from routers.companies import router as companies_router
from routers.customers import router as customers_router
from routers.products import router as products_router
from routers.warehouses import router as warehouses_router
from routers import query
from routers.events import router as events_router
from routers.relationships import router as relationships_router
from routers.graph import router as graph_router
from routers import auth
from routers import assistant
from routers import demo_requests
from routers import imports
from routers.contact import router as contact_router
from routers.account import router as account_router
from routers.summary import router as summary_router
# Pendientes de confirmar en el repositorio: routers.inventory y routers.manage.
# Inclúyelos aquí cuando sus archivos estén en git; si no, el servidor no arranca.

Base.metadata.create_all(bind=engine)
ensure_demo_request_columns(engine)

DEMO_RETENTION_DAYS = 7  # debe coincidir con la política de privacidad


def purge_old_demo_requests() -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=DEMO_RETENTION_DAYS)
    with SessionLocal() as db:
        db.query(DemoRequest).filter(DemoRequest.created_at < cutoff).delete(synchronize_session=False)
        db.commit()


async def _purge_loop() -> None:
    while True:
        try:
            await asyncio.to_thread(purge_old_demo_requests)
        except Exception:
            logging.exception("No se pudo purgar solicitudes antiguas")
        await asyncio.sleep(3600)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    task = asyncio.create_task(_purge_loop())
    yield
    task.cancel()


app = FastAPI(
    lifespan=lifespan,
    title="EDITH Intelligence API",
    version="0.1.0"
)

# Las rutas de empresas exigen sesión
app.include_router(companies_router, dependencies=[Depends(get_current_user)])
app.include_router(customers_router)
app.include_router(products_router)
app.include_router(warehouses_router)
app.include_router(query.router)
app.include_router(events_router)
app.include_router(relationships_router)
app.include_router(graph_router)
app.include_router(auth.router)
app.include_router(assistant.router)
app.include_router(demo_requests.router)
app.include_router(imports.router)
app.include_router(contact_router)
app.include_router(account_router)
app.include_router(summary_router)
# El sitio compilado (npm run build en frontend/) vive en backend/static y no se guarda en git.
# Render y el Dockerfile lo compilan en cada despliegue. En local, sin compilar, la API funciona igual.
STATIC_DIR = Path("static")
INDEX = STATIC_DIR / "index.html"
if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
else:
    logging.getLogger(__name__).warning(
        "No existe backend/static: el sitio no está compilado. Ejecuta 'npm run build' en frontend/."
    )


@app.middleware("http")
async def strip_api_prefix_and_headers(request: Request, call_next):
    # El frontend llama a /api/...; Vite lo quita en desarrollo y aquí se quita en producción.
    path = request.scope["path"]
    if path == "/api" or path.startswith("/api/"):
        request.scope["path"] = path[4:] or "/"
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    return response


@app.get("/", include_in_schema=False)
def root():
    # Si el frontend está compilado se sirve la landing; si no, el mensaje de la API.
    if INDEX.is_file():
        return FileResponse(INDEX)
    return {"message": "EDITH Intelligence API funcionando"}


@app.get("/health")
def health():
    return {"status": "ok"}


# Rutas de React (recargar la página en ellas debe seguir mostrando el sitio).
@app.get("/app", include_in_schema=False)
@app.get("/app/{rest:path}", include_in_schema=False)
@app.get("/privacidad", include_in_schema=False)
@app.get("/login", include_in_schema=False)
def web_app(rest: str = ""):
    if INDEX.is_file():
        return FileResponse(INDEX)
    return JSONResponse(
        {"detail": "Sitio no compilado. Ejecuta 'npm run build' en frontend/."}, status_code=404
    )
