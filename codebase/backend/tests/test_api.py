from __future__ import annotations

from app.rag.generation.generator import AnswerGenerator
import hashlib

from app.rag.models import Chunk, GenerationResult, RetrievalRequest
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


def test_greeting_introduces_tutor_without_retrieval() -> None:
    retriever = EmptyRetriever()
    service = RAGService(
        retriever=retriever,
        generator=AnswerGenerator(),
    )

    response = service.ask("Xin chào")

    assert response.status == "answered"
    assert "VLearn Tutor" in response.answer
    assert "trợ lý AI" in response.answer
    assert response.citations == []
    assert response.retrieval_hits == []
    assert retriever.last_request is None


class SummaryStore:
    def get_chunks(self, *, where=None):
        text = "Nội dung đầy đủ của bài học."
        return [
            Chunk(
                chunk_id="day-01-slide-01-chunk-01",
                document_id="day-01",
                document_title="Day 1",
                session_number=1,
                source_file="day-01.pdf",
                slide_number=1,
                chunk_index=1,
                text=text,
                extraction_method="text",
                content_hash=hashlib.sha256(text.encode()).hexdigest(),
                token_count=6,
            )
        ]


class SummaryRetriever:
    def __init__(self):
        self.vector_store = SummaryStore()
        self.retrieve_called = False

    def retrieve(self, request):
        self.retrieve_called = True
        return []


class SummaryGenerator:
    def __init__(self):
        self.trusted_context = False

    def generate(self, query, hits, **kwargs):
        self.trusted_context = kwargs.get("trusted_context", False)
        return GenerationResult(
            answer="Bản tóm tắt.",
            confidence=1.0,
            abstained=False,
            citations=[],
        )


def test_summary_uses_full_context_but_hides_rag_sources() -> None:
    retriever = SummaryRetriever()
    generator = SummaryGenerator()
    service = RAGService(retriever=retriever, generator=generator)

    response = service.ask(
        "Tóm tắt bài này",
        document_id="day-01",
        max_slide=1,
    )

    assert response.answer == "Bản tóm tắt."
    assert response.citations == []
    assert response.retrieval_hits == []
    assert generator.trusted_context is True
    assert retriever.retrieve_called is False
