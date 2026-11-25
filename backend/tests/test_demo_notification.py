import os
from types import SimpleNamespace

os.environ.setdefault("DATABASE_URL", "sqlite://")

from routers import demo_requests


class FakeSMTP:
    sent = []

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def starttls(self, **kwargs):
        pass

    def login(self, user, password):
        pass

    def send_message(self, message):
        FakeSMTP.sent.append(message)


def test_notification_replies_to_requester_and_shows_message(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_USER", "ventas@example.com")
    monkeypatch.setenv("DEMO_REQUEST_EMAIL", "ventas@example.com")
    monkeypatch.delenv("SMTP_FROM", raising=False)
    monkeypatch.setattr(demo_requests.smtplib, "SMTP", FakeSMTP)
    FakeSMTP.sent.clear()

    demo = SimpleNamespace(
        id=7, name="Ana Ruiz", email="ana@cliente.com", company_name="Ferretería Sol",
        job_title="Gerente", sector="retail", company_size=None,
        need="Controlar inventario en tres bodegas", message="¿Pueden llamarme el lunes?",
    )

    assert demo_requests._send_notification(demo) == "sent"
    message = FakeSMTP.sent[0]
    assert message["Reply-To"] == "ana@cliente.com"
    assert "Ferretería Sol" in message["Subject"]
    body = message.get_content()
    assert "¿Pueden llamarme el lunes?" in body
    assert "Controlar inventario en tres bodegas" in body
