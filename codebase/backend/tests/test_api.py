from pathlib import Path

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app


def test_health_and_empty_chat(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("VECTOR_STORE_PATH", str(tmp_path / "store.json"))
    get_settings.cache_clear()
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"
        response = client.post("/api/chat", json={"question": "Attention là gì?"})
        assert response.status_code == 200
        assert response.json()["status"] == "no_context"
