from app.rag.models import SearchHit
from app.rag.retrieval.reranker import rerank
from app.rag.vector_store import JsonVectorStore


def retrieve(
    question: str,
    store: JsonVectorStore,
    top_k: int,
    session_ids: list[str] | None = None,
    file_names: list[str] | None = None,
) -> list[SearchHit]:
    initial = store.search(question, max(top_k * 2, top_k), session_ids, file_names)
    return rerank(question, initial)[:top_k]
