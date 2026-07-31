from __future__ import annotations

import re

from app.rag.models import Citation, SearchHit


def _excerpt(text: str, maximum_characters: int = 240) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= maximum_characters:
        return compact
    shortened = compact[: maximum_characters - 1].rsplit(" ", 1)[0]
    return f"{shortened}…"


def build_citations(
    hits: list[SearchHit],
    *,
    maximum_citations: int = 5,
) -> list[Citation]:
    citations: list[Citation] = []
    seen_chunk_ids: set[str] = set()
    for hit in hits:
        if hit.chunk.chunk_id in seen_chunk_ids:
            continue
        seen_chunk_ids.add(hit.chunk.chunk_id)
        citations.append(
            Citation(
                source_file=hit.chunk.source_file,
                document_id=hit.chunk.document_id,
                document_title=hit.chunk.document_title,
                slide_number=hit.chunk.slide_number,
                chunk_id=hit.chunk.chunk_id,
                excerpt=_excerpt(hit.chunk.text),
            )
        )
        if len(citations) >= maximum_citations:
            break
    return citations


def citations_belong_to_hits(
    citations: list[Citation], hits: list[SearchHit]
) -> bool:
    valid_chunk_ids = {hit.chunk.chunk_id for hit in hits}
    return all(
        citation.chunk_id in valid_chunk_ids for citation in citations
    )
