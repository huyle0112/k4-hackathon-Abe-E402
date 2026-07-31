from __future__ import annotations

import hashlib

from app.rag.evaluation import evaluate_cases
from app.rag.models import (
    ChatResponse,
    Chunk,
    Citation,
    ExpectedSource,
    GoldenCase,
    SearchHit,
)


def _response(*, abstained: bool) -> ChatResponse:
    text = "Nguồn kiểm thử."
    chunk = Chunk(
        chunk_id="day-01-slide-01-chunk-01",
        document_id="day-01",
        document_title="Day 1",
        session_number=1,
        source_file="day-01.pdf",
        slide_number=1,
        chunk_index=1,
        text=text,
        extraction_method="text",
        content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        token_count=3,
    )
    hit = SearchHit(chunk=chunk, score=0.8, rank=1)
    citations = (
        []
        if abstained
        else [
            Citation(
                source_file=chunk.source_file,
                document_id=chunk.document_id,
                document_title=chunk.document_title,
                slide_number=chunk.slide_number,
                chunk_id=chunk.chunk_id,
                excerpt=text,
            )
        ]
    )
    return ChatResponse(
        answer="Không đủ nguồn." if abstained else "Câu trả lời.",
        confidence=0.0 if abstained else 0.8,
        abstained=abstained,
        citations=citations,
        retrieval_hits=[] if abstained else [hit],
    )


class StubService:
    def ask(
        self,
        query: str,
        *,
        session_numbers: list[int] | None = None,
        top_k: int = 5,
    ) -> ChatResponse:
        del session_numbers, top_k
        return _response(abstained="ngoài phạm vi" in query)


def test_evaluator_scores_retrieval_citation_and_abstention() -> None:
    cases = [
        GoldenCase(
            case_id="in-scope",
            category="single-session",
            query="Câu hỏi trong tài liệu",
            expected_abstain=False,
            expected_sources=[
                ExpectedSource(document_id="day-01", slide_number=1)
            ],
        ),
        GoldenCase(
            case_id="out-of-scope",
            category="out-of-scope",
            query="Câu hỏi ngoài phạm vi",
            expected_abstain=True,
        ),
    ]

    report = evaluate_cases(StubService(), cases)

    assert report.pass_rate == 1.0
    assert report.abstention_accuracy == 1.0
    assert report.retrieval_hit_rate == 1.0
    assert report.citation_hit_rate == 1.0
