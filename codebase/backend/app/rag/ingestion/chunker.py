import hashlib

from app.rag.embeddings import embed
from app.rag.ingestion.normalizer import normalize_text
from app.rag.models import Chunk


def chunk_page(
    text: str,
    file_name: str,
    session_id: str,
    page: int,
    max_chars: int = 1200,
    overlap: int = 160,
) -> list[Chunk]:
    clean = normalize_text(text)
    if not clean:
        return []
    chunks: list[Chunk] = []
    start = 0
    while start < len(clean):
        end = min(len(clean), start + max_chars)
        if end < len(clean):
            boundary = clean.rfind(" ", start, end)
            if boundary > start + max_chars // 2:
                end = boundary
        content = clean[start:end].strip()
        digest = hashlib.sha1(f"{session_id}:{file_name}:{page}:{start}".encode()).hexdigest()[:16]
        chunks.append(Chunk(
            id=digest,
            text=content,
            file_name=file_name,
            session_id=session_id,
            page=page,
            slide=page,
            embedding=embed(content),
        ))
        if end >= len(clean):
            break
        start = max(start + 1, end - overlap)
    return chunks
