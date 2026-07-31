from app.rag.models import Citation, SearchHit


def build_citations(hits: list[SearchHit], limit: int = 3) -> list[Citation]:
    result: list[Citation] = []
    seen: set[tuple[str, int]] = set()
    for hit in hits:
        key = (hit.chunk.file_name, hit.chunk.page)
        if key in seen:
            continue
        seen.add(key)
        excerpt = hit.chunk.text[:240].strip()
        result.append(Citation(
            file_name=hit.chunk.file_name,
            session_id=hit.chunk.session_id,
            page=hit.chunk.page,
            slide=hit.chunk.slide,
            excerpt=excerpt + ("…" if len(hit.chunk.text) > 240 else ""),
        ))
        if len(result) >= limit:
            break
    return result
