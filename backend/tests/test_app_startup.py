"""Arranca la aplicación completa (main.py) para detectar imports rotos antes de desplegar.

backend/static no se guarda en git (lo genera `npm run build` en frontend/), así que cada
prueba fija su propio directorio de trabajo: uno con un sitio compilado de ejemplo y otro sin él.
"""
import os

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient

SITE_PATHS = ("/", "/login", "/privacidad", "/app", "/app/customers")


def _fake_build(root):
    assets = root / "static" / "assets"
    assets.mkdir(parents=True)
    (root / "static" / "index.html").write_text(
        '<!doctype html><div id="root"></div><script src="/static/assets/app.js"></script>',
        encoding="utf-8",
    )
    (assets / "app.js").write_text("console.log('ok');", encoding="utf-8")


def test_main_app_starts_and_serves_site_and_api(tmp_path, monkeypatch):
    import main

    _fake_build(tmp_path)
    monkeypatch.chdir(tmp_path)
    with TestClient(main.app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        assert client.get("/api/health").json() == {"status": "ok"}
        for path in SITE_PATHS:
            response = client.get(path)
            assert response.status_code == 200, path
            assert "text/html" in response.headers["content-type"], path
            assert 'id="root"' in response.text, path
        assert client.get("/static/assets/app.js").status_code == 200
        assert client.get("/").headers["x-frame-options"] == "DENY"


def test_main_app_starts_without_compiled_site(tmp_path, monkeypatch):
    import main

    monkeypatch.chdir(tmp_path)  # sin static/
    with TestClient(main.app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        assert client.get("/").json() == {"message": "EDITH Intelligence API funcionando"}
        for path in SITE_PATHS[1:]:
            response = client.get(path)
            assert response.status_code == 503, path
            assert "npm run build" in response.text, path
        assert client.get("/static/assets/app.js").status_code == 404
