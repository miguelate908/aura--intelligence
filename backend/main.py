from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from database import engine, Base

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

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AURA Intelligence API",
    version="0.1.0"
)

app.include_router(companies_router)
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
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return {"message": "AURA Intelligence API funcionando"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/app", include_in_schema=False)
def web_app():
    return FileResponse("static/index.html")
