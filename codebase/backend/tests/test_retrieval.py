from pathlib import Path

from app.rag.embeddings import embed
from app.rag.models import Chunk
from app.rag.retrieval.retriever import retrieve
from app.rag.vector_store import JsonVectorStore


def test_retrieval_respects_session_scope(tmp_path: Path):
    store = JsonVectorStore(tmp_path / "store.json")
    chunks = [
        Chunk(id="a", text="Transformer dùng cơ chế attention", file_name="a.pdf", session_id="day-01", page=1, embedding=embed("Transformer dùng cơ chế attention")),
    ]
    store.replace_session("day-01", chunks)
    assert retrieve("attention", store, 3, ["day-01"])[0].chunk.id == "a"
    assert retrieve("attention", store, 3, ["day-02"]) == []
