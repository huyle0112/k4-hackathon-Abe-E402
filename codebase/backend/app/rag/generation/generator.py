from __future__ import annotations

import re
from typing import Protocol

from app.rag.generation.citations import (
    build_citations,
    citations_belong_to_hits,
)
from app.rag.generation.prompt import build_generation_prompt
from app.rag.models import GenerationResult, SearchHit


class TextGenerationProvider(Protocol):
    @property
    def name(self) -> str: ...

    def generate(self, prompt: str) -> str: ...


class StaticTextGenerationProvider:
    """Deterministic provider for tests and integration development."""

    def __init__(self, response: str) -> None:
        self.response = response

    @property
    def name(self) -> str:
        return "static"

    def generate(self, prompt: str) -> str:
        del prompt
        return self.response


class AnswerGenerator:
    def __init__(
        self,
        *,
        provider: TextGenerationProvider | None = None,
        abstention_threshold: float = 0.12,
        minimum_lexical_coverage: float = 0.4,
        minimum_vector_score: float = 0.28,
        maximum_citations: int = 5,
    ) -> None:
        self.provider = provider
        self.abstention_threshold = abstention_threshold
        self.minimum_lexical_coverage = minimum_lexical_coverage
        self.minimum_vector_score = minimum_vector_score
        self.maximum_citations = maximum_citations

    def generate(
        self, query: str, hits: list[SearchHit]
    ) -> GenerationResult:
        if not hits:
            return self._abstain("Không tìm thấy nguồn liên quan.")

        confidence = self._confidence(hits)
        if hits[0].score < self.abstention_threshold:
            return self._abstain(
                "Nguồn tìm được chưa đạt ngưỡng liên quan.",
                confidence=confidence,
            )
        top_lexical = hits[0].lexical_score or 0.0
        top_vector = hits[0].vector_score or 0.0
        if (
            top_lexical < self.minimum_lexical_coverage
            and top_vector < self.minimum_vector_score
        ):
            return self._abstain(
                "Nguồn không bao phủ đủ các khái niệm chính trong câu hỏi.",
                confidence=confidence,
            )

        citations = build_citations(
            hits, maximum_citations=self.maximum_citations
        )
        if not citations or not citations_belong_to_hits(citations, hits):
            return self._abstain(
                "Không thể tạo citation hợp lệ.",
                confidence=confidence,
            )

        if self.provider is not None:
            answer = self.provider.generate(
                build_generation_prompt(query, hits)
            ).strip()
        else:
            answer = self._extractive_answer(hits)

        if not answer:
            return self._abstain(
                "Không thể tạo câu trả lời từ nguồn hiện có.",
                confidence=confidence,
            )

        return GenerationResult(
            answer=answer,
            confidence=confidence,
            abstained=False,
            citations=citations,
        )

    @staticmethod
    def _confidence(hits: list[SearchHit]) -> float:
        scores = [max(0.0, min(1.0, hit.score)) for hit in hits[:3]]
        top_score = scores[0]
        mean_score = sum(scores) / len(scores)
        unique_documents = len(
            {hit.chunk.document_id for hit in hits[:3]}
        )
        source_support = min(1.0, unique_documents / 2)
        margin = (
            max(0.0, top_score - scores[1]) if len(scores) > 1 else top_score
        )
        heuristic = (
            top_score * 0.55
            + mean_score * 0.25
            + source_support * 0.10
            + min(1.0, margin * 2) * 0.10
        )
        return round(max(0.0, min(1.0, heuristic)), 4)

    @staticmethod
    def _extractive_answer(hits: list[SearchHit]) -> str:
        statements: list[str] = []
        for hit in hits[:3]:
            compact = re.sub(r"\s+", " ", hit.chunk.text).strip()
            sentences = re.split(r"(?<=[.!?])\s+", compact)
            excerpt = " ".join(sentences[:2]).strip()
            if len(excerpt) > 500:
                excerpt = f"{excerpt[:497].rsplit(' ', 1)[0]}…"
            if excerpt:
                statements.append(
                    f"- {excerpt} "
                    f"[{hit.chunk.source_file}, slide "
                    f"{hit.chunk.slide_number}]"
                )
        if not statements:
            return ""
        return "Theo các slide được truy xuất:\n\n" + "\n".join(statements)

    @staticmethod
    def _abstain(
        reason: str, *, confidence: float = 0.0
    ) -> GenerationResult:
        return GenerationResult(
            answer=(
                "Mình chưa có đủ căn cứ trong tài liệu để trả lời câu hỏi này."
            ),
            confidence=confidence,
            abstained=True,
            citations=[],
            reason=reason,
        )
