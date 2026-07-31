from __future__ import annotations

from app.rag.embeddings import EmbeddingProvider
from app.rag.models import RetrievalRequest, SearchHit
from app.rag.retrieval.filters import build_session_filter
from app.rag.retrieval.reranker import BaselineReranker
from app.rag.vector_store import ChromaVectorStore


class Retriever:
    def __init__(
        self,
        *,
        embedding_provider: EmbeddingProvider,
        vector_store: ChromaVectorStore,
        reranker: BaselineReranker | None = None,
        candidate_k: int = 20,
        score_threshold: float = 0.12,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.reranker = reranker or BaselineReranker()
        self.candidate_k = candidate_k
        self.score_threshold = score_threshold

    def retrieve(self, request: RetrievalRequest) -> list[SearchHit]:
        query_embedding = self.embedding_provider.embed_query(request.query)
        candidates = self.vector_store.query(
            query_embedding,
            n_results=max(self.candidate_k, request.top_k * 3),
            where=build_session_filter(request.session_numbers),
        )
        return self.reranker.rerank(
            request.query,
            candidates,
            top_k=request.top_k,
            score_threshold=self.score_threshold,
        )
