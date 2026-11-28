"""Arranca la aplicación completa (main.py) para detectar imports rotos antes de desplegar."""
import importlib
import os
import sys

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient

SITE_PATHS = ("/", "/login", "/privacidad", "/app/customers")


def _load_main(monkeypatch, workdir):
    # main.py busca el sitio en ./static, relativo a la carpeta desde la que arranca uvicorn.
    monkeypatch.chdir(workdir)
    sys.modules.pop("main", None)
    return importlib.import_module("main")


def test_main_app_starts_and_serves_site_and_api(monkeypatch, tmp_path):
    # backend/static ya no está en git: se simula un sitio compilado.
    (tmp_path / "static" / "assets").mkdir(parents=True)
    (tmp_path / "static" / "index.html").write_text(
        '<!doctype html><script src="/static/assets/app.js"></script>', encoding="utf-8"
    )
    (tmp_path / "static" / "assets" / "app.js").write_text("console.log(1)", encoding="utf-8")
    main = _load_main(monkeypatch, tmp_path)

    with TestClient(main.app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        assert client.get("/api/health").json() == {"status": "ok"}
        for path in SITE_PATHS:
            response = client.get(path)
            assert response.status_code == 200, path
            assert "text/html" in response.headers["content-type"], path
        assert client.get("/static/assets/app.js").status_code == 200
        assert client.get("/").headers["x-frame-options"] == "DENY"


def test_head_requests_for_uptime_monitors(monkeypatch, tmp_path):
    # Los monitores externos comprueban la disponibilidad con HEAD; antes respondía 405.
    (tmp_path / "static").mkdir()
    (tmp_path / "static" / "index.html").write_text("<!doctype html><p>EDITH</p>", encoding="utf-8")
    main = _load_main(monkeypatch, tmp_path)

    with TestClient(main.app) as client:
        for path in ("/health", "/api/health") + SITE_PATHS:
            response = client.head(path)
            assert response.status_code == 200, path
            assert response.content == b"", path
        assert "text/html" in client.head("/").headers["content-type"]
        assert client.head("/").headers["x-frame-options"] == "DENY"
        # HEAD no abre endpoints que antes no existían ni salta la autenticación.
        assert client.head("/customers/").status_code in (401, 405)


def test_main_app_starts_without_compiled_site(monkeypatch, tmp_path):
    main = _load_main(monkeypatch, tmp_path)

    with TestClient(main.app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        assert client.get("/").json() == {"message": "EDITH Intelligence API funcionando"}
        for path in SITE_PATHS[1:]:
            response = client.get(path)
            assert response.status_code == 404, path
            assert "npm run build" in response.json()["detail"], path
