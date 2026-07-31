from __future__ import annotations

from app.rag.generation.generator import AnswerGenerator
from app.rag.models import RetrievalRequest
from app.rag.service import RAGService


class EmptyRetriever:
    def __init__(self) -> None:
        self.last_request: RetrievalRequest | None = None

    def retrieve(self, request: RetrievalRequest) -> list:
        self.last_request = request
        return []


def test_rag_service_returns_structured_abstention() -> None:
    retriever = EmptyRetriever()
    service = RAGService(
        retriever=retriever,
        generator=AnswerGenerator(),
    )

    response = service.ask(
        "Nội dung ngoài tài liệu",
        session_numbers=[2, 1, 1],
        top_k=3,
    )

    assert response.abstained
    assert response.retrieval_hits == []
    assert retriever.last_request is not None
    assert retriever.last_request.session_numbers == [1, 2]
    assert retriever.last_request.top_k == 3

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
