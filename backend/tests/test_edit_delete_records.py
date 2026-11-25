"""Editar y eliminar clientes, productos y bodegas, respetando el aislamiento entre empresas."""
import os

os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

import test_auth_tenant_isolation as base
from test_auth_tenant_isolation import client, register
from models import Event

CASES = [
    ("/customers/", {"name": "Cliente A"}, {"name": "Cliente A editado", "email": "a@ejemplo.test", "phone": "300"}, "customer"),
    ("/products/", {"sku": "SKU-1", "name": "Producto A", "price": 10}, {"sku": "SKU-1B", "name": "Producto A2", "price": 25.5}, "product"),
    ("/warehouses/", {"name": "Bodega A"}, {"name": "Bodega A2", "location": "Bello"}, "warehouse"),
]


def setup_function():
    os.environ["DISABLE_RATE_LIMIT"] = "1"  # registra varias empresas seguidas
    base.setup_function()


def teardown_function():
    os.environ.pop("DISABLE_RATE_LIMIT", None)


@pytest.mark.parametrize("path,create,update,entity", CASES)
def test_owner_can_edit_and_delete_and_other_company_cannot(path, create, update, entity):
    a = {"Authorization": f"Bearer {register('Empresa A', 'edit-a@example.com')}"}
    b = {"Authorization": f"Bearer {register('Empresa B', 'edit-b@example.com')}"}
    created = client.post(path, headers=a, json={"company_id": 1, **create})
    assert created.status_code == 200, created.text
    rid = created.json()["id"]

    # Otra empresa no puede ni editar ni eliminar (404, como si no existiera).
    assert client.put(f"{path}{rid}", headers=b, json=update).status_code == 404
    assert client.delete(f"{path}{rid}", headers=b).status_code == 404

    edited = client.put(f"{path}{rid}", headers=a, json=update)
    assert edited.status_code == 200, edited.text
    for k, v in update.items():
        assert edited.json()[k] == v
    assert edited.json()["company_id"] == 1  # el cuerpo no permite cambiar de empresa

    graph_before = client.get(f"/relationships/entity/{entity}/{rid}", headers=a).json()
    assert len(graph_before) == 1

    assert client.delete(f"{path}{rid}", headers=a).status_code == 204
    assert rid not in [r["id"] for r in client.get(path, headers=a).json()]
    assert client.get(f"/relationships/entity/{entity}/{rid}", headers=a).json() == []
    types = [e["event_type"] for e in client.get("/events/", headers=a).json()]
    assert f"{entity}.updated" in types and f"{entity}.deleted" in types


def test_update_validates_payload():
    a = {"Authorization": f"Bearer {register('Empresa A', 'val-a@example.com')}"}
    rid = client.post("/customers/", headers=a, json={"company_id": 1, "name": "X"}).json()["id"]
    assert client.put(f"/customers/{rid}", headers=a, json={"name": ""}).status_code == 422
    assert client.put(f"/customers/{rid}", headers=a, json={"name": "X", "email": "malo"}).status_code == 422
    assert client.put(f"/customers/{rid}", headers={}, json={"name": "Y"}).status_code == 401


@pytest.mark.parametrize("operation", ["update", "delete"])
def test_event_failure_rolls_back_record_and_relationships(operation):
    headers = {"Authorization": f"Bearer {register('Empresa A', 'rollback@example.com')}"}
    created = client.post("/customers/", headers=headers, json={"company_id": 1, "name": "Original"})
    assert created.status_code == 200
    rid = created.json()["id"]
    url = f"/customers/{rid}"
    graph_url = f"/relationships/entity/customer/{rid}"
    relationships = client.get(graph_url, headers=headers).json()
    events = client.get("/events/", headers=headers).json()
    assert len(relationships) == 1

    def invalidate_event(mapper, connection, target):
        target.event_type = None  # La base rechaza el evento por la restricción NOT NULL.

    event.listen(Event, "before_insert", invalidate_event)
    try:
        with pytest.raises(IntegrityError):
            if operation == "update":
                client.put(url, headers=headers, json={"name": "Modificado"})
            else:
                client.delete(url, headers=headers)
    finally:
        event.remove(Event, "before_insert", invalidate_event)

    assert client.get(url, headers=headers).json()["name"] == "Original"
    assert client.get(graph_url, headers=headers).json() == relationships
    assert client.get("/events/", headers=headers).json() == events
