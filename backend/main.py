from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from database import engine, Base

from core.security import get_current_user
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
from routers.inventory import router as inventory_router
from routers.manage import router as manage_router
from routers.contact import router as contact_router
from routers.account import router as account_router
from routers import demo_requests
from routers import imports

Base.metadata.create_all(bind=engine)

DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


class StripApiPrefix:
    """Permite llamar a la API como /api/... (producción) o sin prefijo (pruebas y /docs)."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket") and scope["path"].startswith("/api/"):
            scope = dict(scope)
            scope["path"] = scope["path"][4:]
            if scope.get("raw_path"):
                scope["raw_path"] = scope["raw_path"][4:]
        await self.app(scope, receive, send)


app = FastAPI(
    title="EDITH Intelligence API",
    version="0.1.0"
)
app.add_middleware(StripApiPrefix)

# Las rutas de empresas ahora exigen sesión (antes eran públicas)
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
app.include_router(inventory_router)
app.include_router(manage_router)
app.include_router(contact_router)
app.include_router(account_router)
app.include_router(demo_requests.router)
app.include_router(imports.router)

if Path("static").is_dir():
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
def health():
    return {"status": "ok"}


if DIST.is_dir():
    # Sitio compilado (npm run build): la API y la página viven en el mismo servidor
    if (DIST / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    def spa(rest: str = ""):
        return FileResponse(DIST / "index.html")

    for _p in ("/", "/login", "/privacidad", "/app", "/app/{rest:path}"):
        app.add_api_route(_p, spa, methods=["GET"], include_in_schema=False)
else:
    @app.get("/")
    def root():
        return {"message": "EDITH Intelligence API funcionando"}

    @app.get("/app", include_in_schema=False)
    def web_app():
        return FileResponse("static/index.html")
