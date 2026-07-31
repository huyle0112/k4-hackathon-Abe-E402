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


def build_citations_for_chunk_ids(
    hits: list[SearchHit],
    cited_chunk_ids: list[str],
    *,
    maximum_citations: int = 5,
) -> list[Citation]:
    """Resolve model-proposed IDs only against the exact supplied hits."""

    hits_by_id = {hit.chunk.chunk_id: hit for hit in hits}
    resolved_hits: list[SearchHit] = []
    seen_chunk_ids: set[str] = set()
    for chunk_id in cited_chunk_ids:
        if chunk_id in seen_chunk_ids:
            continue
        hit = hits_by_id.get(chunk_id)
        if hit is None:
            continue
        seen_chunk_ids.add(chunk_id)
        resolved_hits.append(hit)
        if len(resolved_hits) >= maximum_citations:
            break
    return build_citations(
        resolved_hits,
        maximum_citations=maximum_citations,
    )


def citations_belong_to_hits(
    citations: list[Citation], hits: list[SearchHit]
) -> bool:
    valid_chunk_ids = {hit.chunk.chunk_id for hit in hits}
    return all(
        citation.chunk_id in valid_chunk_ids for citation in citations
    )
