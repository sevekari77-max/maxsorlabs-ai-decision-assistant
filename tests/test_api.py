import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

os.environ["GEMINI_API_KEY"] = "test-key"
os.environ["JWT_SECRET"] = (
    "test-secret-key-that-is-at-least-32-characters-long"
)

from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_me_requires_authentication():
    response = client.get("/me")

    assert response.status_code == 401


def test_tickets_require_authentication():
    response = client.get("/tickets")

    assert response.status_code == 401


def test_ticket_creation_requires_authentication():
    response = client.post(
        "/tickets",
        json={
            "message": "My package arrived damaged yesterday."
        },
    )

    assert response.status_code == 401


def test_invalid_token_is_rejected():
    response = client.get(
        "/me",
        headers={
            "Authorization": "Bearer invalid-token"
        },
    )

    assert response.status_code == 401


def test_register_validation():
    response = client.post(
        "/register",
        json={
            "email": "not-an-email",
            "password": "short",
        },
    )

    assert response.status_code == 422