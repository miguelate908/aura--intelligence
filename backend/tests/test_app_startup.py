"""Arranca la aplicación completa (main.py) para detectar imports rotos antes de desplegar."""
import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-that-is-long-enough-32-characters")

from fastapi.testclient import TestClient


def test_main_app_starts_and_serves_site_and_api():
    import main

    with TestClient(main.app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        assert client.get("/api/health").json() == {"status": "ok"}
        for path in ("/", "/login", "/privacidad", "/app/customers"):
            response = client.get(path)
            assert response.status_code == 200, path
            assert "text/html" in response.headers["content-type"], path
        assert client.get("/").headers["x-frame-options"] == "DENY"
