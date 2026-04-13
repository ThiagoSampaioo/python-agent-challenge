from fastapi.testclient import TestClient

from app.main import app
from app.core.constants import FALLBACK_ANSWER

client = TestClient(app)


def test_messages_requires_message_field():
    response = client.post("/messages", json={})
    assert response.status_code == 422


def test_messages_rejects_blank_message():
    response = client.post("/messages", json={"message": "   "})
    assert response.status_code == 422


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}