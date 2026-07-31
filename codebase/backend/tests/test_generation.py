from __future__ import annotations

import hashlib

from app.rag.generation.citations import citations_belong_to_hits
from app.rag.generation.generator import (
    AnswerGenerator,
    StaticTextGenerationProvider,
)
from app.rag.models import Chunk, SearchHit


def _hit(score: float = 0.8) -> SearchHit:
    text = "Context là lượng nội dung mô hình có thể nhìn thấy khi trả lời."
    chunk = Chunk(
        chunk_id="day-01-slide-14-chunk-01",
        document_id="day-01",
        document_title="AI Foundation",
        session_number=1,
        source_file="day-01.pdf",
        slide_number=14,
        chunk_index=1,
        text=text,
        extraction_method="text",
        content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        token_count=len(text.split()),
    )
    return SearchHit(
        chunk=chunk,
        score=score,
        vector_score=score,
        lexical_score=0.8,
        rank=1,
    )


def test_extractive_generation_includes_valid_citation() -> None:
    hit = _hit()

    result = AnswerGenerator().generate("Context là gì?", [hit])

    assert not result.abstained
    assert result.citations[0].slide_number == 14
    assert citations_belong_to_hits(result.citations, [hit])
    assert "slide 14" in result.answer


def test_generation_abstains_without_sources() -> None:
    result = AnswerGenerator().generate("Câu hỏi ngoài phạm vi", [])

    assert result.abstained
    assert result.confidence == 0.0
    assert result.citations == []


def test_generation_abstains_when_evidence_coverage_is_low() -> None:
    weak_hit = _hit(score=0.2).model_copy(
        update={"vector_score": 0.2, "lexical_score": 0.1}
    )

    result = AnswerGenerator().generate(
        "Công thức nấu món ăn ngoài phạm vi?", [weak_hit]
    )

    assert result.abstained
    assert result.citations == []


def test_static_provider_can_replace_extractive_fallback() -> None:
    provider = StaticTextGenerationProvider("Câu trả lời kiểm thử.")

    result = AnswerGenerator(provider=provider).generate(
        "Context là gì?", [_hit()]
    )

    assert result.answer == "Câu trả lời kiểm thử."
    assert not result.abstained
