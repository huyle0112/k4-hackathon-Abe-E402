from __future__ import annotations

import re
import unicodedata

from app.rag.models import SearchHit


_WORD = re.compile(r"\w+", re.UNICODE)
_VIETNAMESE_STOPWORDS = {
    "ai",
    "bị",
    "các",
    "có",
    "của",
    "cho",
    "được",
    "gì",
    "khi",
    "là",
    "một",
    "những",
    "nào",
    "theo",
    "trong",
    "tại",
    "và",
    "với",
}


def _terms(text: str) -> set[str]:
    normalized = unicodedata.normalize("NFC", text).lower()
    return {
        term
        for term in _WORD.findall(normalized)
        if len(term) > 1 and term not in _VIETNAMESE_STOPWORDS
    }


def lexical_overlap(query: str, document: str) -> float:
    query_terms = _terms(query)
    if not query_terms:
        return 0.0
    document_terms = _terms(document)
    return len(query_terms & document_terms) / len(query_terms)


class BaselineReranker:
    def __init__(
        self,
        *,
        vector_weight: float = 0.65,
        lexical_weight: float = 0.35,
    ) -> None:
        if vector_weight < 0 or lexical_weight < 0:
            raise ValueError("Reranker weights must be non-negative")
        if vector_weight + lexical_weight == 0:
            raise ValueError("At least one reranker weight must be positive")
        total = vector_weight + lexical_weight
        self.vector_weight = vector_weight / total
        self.lexical_weight = lexical_weight / total

    def rerank(
        self,
        query: str,
        hits: list[SearchHit],
        *,
        top_k: int,
        score_threshold: float,
    ) -> list[SearchHit]:
        rescored: list[SearchHit] = []
        seen_hashes: set[str] = set()

        for hit in hits:
            if hit.chunk.content_hash in seen_hashes:
                continue
            seen_hashes.add(hit.chunk.content_hash)
            body_overlap = lexical_overlap(query, hit.chunk.text)
            first_line = hit.chunk.text.splitlines()[0]
            title_overlap = lexical_overlap(query, first_line)
            lexical_score = body_overlap * 0.7 + title_overlap * 0.3
            vector_score = max(0.0, hit.vector_score or hit.score)
            score = (
                self.vector_weight * vector_score
                + self.lexical_weight * lexical_score
            )
            if score < score_threshold:
                continue
            rescored.append(
                hit.model_copy(
                    update={
                        "score": score,
                        "vector_score": vector_score,
                        "lexical_score": lexical_score,
                    }
                )
            )

        rescored.sort(
            key=lambda hit: (
                hit.score,
                hit.lexical_score or 0.0,
                -hit.chunk.slide_number,
            ),
            reverse=True,
        )
        selected = rescored[:top_k]
        return [
            hit.model_copy(update={"rank": rank})
            for rank, hit in enumerate(selected, start=1)
        ]
