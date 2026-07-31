from pathlib import Path

from app.rag.ingestion.chunker import chunk_page
from app.rag.ingestion.pdf_loader import load_pdf
from app.rag.vector_store import JsonVectorStore


def index_pdf(path: Path, session_id: str, store: JsonVectorStore) -> int:
    chunks = [
        chunk
        for page in load_pdf(path)
        for chunk in chunk_page(page.text, path.name, session_id, page.number)
    ]
    return store.replace_session(session_id, chunks)
