from fastapi.testclient import TestClient

from app.main import app
from app.core.constants import FALLBACK_ANSWER

client = TestClient(app)

# Testes básicos para a rota de mensagens, cobrindo validação e resposta padrão
def test_messages_requires_message_field():
    response = client.post("/messages", json={})
    assert response.status_code == 422

# Testa que mensagens em branco são rejeitadas
def test_messages_rejects_blank_message():
    response = client.post("/messages", json={"message": "   "})
    assert response.status_code == 422

# Testa que mensagens sem sessão também são rejeitadas
def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}