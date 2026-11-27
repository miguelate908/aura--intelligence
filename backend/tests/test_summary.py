"""El resumen del panel cuenta solo los registros de la empresa con sesión."""
import os

os.environ["DATABASE_URL"] = "sqlite://"

import test_auth_tenant_isolation as base
from test_auth_tenant_isolation import client, register
from routers import summary

if not any(getattr(r, "path", "").startswith("/summary") for r in base.app.routes):
    base.app.include_router(summary.router)


def setup_function():
    os.environ["DISABLE_RATE_LIMIT"] = "1"
    base.setup_function()


def teardown_function():
    os.environ.pop("DISABLE_RATE_LIMIT", None)


def test_summary_counts_only_own_company_and_limits_events():
    a = {"Authorization": f"Bearer {register('Empresa A', 'sum-a@example.com')}"}
    b = {"Authorization": f"Bearer {register('Empresa B', 'sum-b@example.com')}"}
    for i in range(3):
        assert client.post("/customers/", headers=a, json={"company_id": 1, "name": f"C{i}"}).status_code == 200
    for i in range(4):
        assert client.post("/products/", headers=a, json={"company_id": 1, "sku": f"S{i}", "name": f"P{i}", "price": 1}).status_code == 200
    assert client.post("/warehouses/", headers=a, json={"company_id": 1, "name": "W"}).status_code == 200
    assert client.post("/customers/", headers=b, json={"company_id": 2, "name": "Otro"}).status_code == 200

    r = client.get("/summary/", headers=a)
    assert r.status_code == 200, r.text
    body = r.json()
    events_a = client.get("/events/", headers=a).json()
    assert body["counts"] == {"customers": 3, "products": 4, "warehouses": 1, "events": len(events_a)}
    assert len(body["recent_events"]) == 5
    # Lo último creado fue la bodega; el desempate por id ordena eventos del mismo segundo.
    assert body["recent_events"][0]["event_type"] == "warehouse.created"
    assert all("Otro" not in (e["description"] or "") for e in body["recent_events"])

    rb = client.get("/summary/", headers=b).json()
    assert rb["counts"]["customers"] == 1 and rb["counts"]["products"] == 0


def test_summary_requires_session():
    assert client.get("/summary/").status_code == 401
