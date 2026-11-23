from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_empty_message():
    response = client.post(
        "/chat",
        json={"message": ""}
    )

    assert response.status_code == 422


def test_chat_missing_message():
    response = client.post(
        "/chat",
        json={}
    )

    assert response.status_code == 422