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
        minimum_session_evidence: int = 1,
    ) -> None:
        if candidate_k < 1:
            raise ValueError("candidate_k must be positive")
        if minimum_session_evidence < 1:
            raise ValueError("minimum_session_evidence must be positive")
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.reranker = reranker or BaselineReranker()
        self.candidate_k = candidate_k
        self.score_threshold = score_threshold
        self.minimum_session_evidence = minimum_session_evidence

    def retrieve(self, request: RetrievalRequest) -> list[SearchHit]:
        query_embedding = self.embedding_provider.embed_query(request.query)
        if request.session_numbers and len(request.session_numbers) >= 2:
            return self._retrieve_cross_session(
                request,
                query_embedding,
            )
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

    def _retrieve_cross_session(
        self,
        request: RetrievalRequest,
        query_embedding: list[float],
    ) -> list[SearchHit]:
        session_numbers = request.session_numbers or []
        candidates_by_id: dict[str, SearchHit] = {}
        candidates_per_session = max(
            self.candidate_k,
            request.top_k * 3,
            self.minimum_session_evidence,
        )
        for session_number in session_numbers:
            session_candidates = self.vector_store.query(
                query_embedding,
                n_results=candidates_per_session,
                where=build_session_filter([session_number]),
            )
            for candidate in session_candidates:
                candidates_by_id.setdefault(
                    candidate.chunk.chunk_id,
                    candidate,
                )

        if not candidates_by_id:
            return []

        reranked = self.reranker.rerank(
            request.query,
            list(candidates_by_id.values()),
            top_k=len(candidates_by_id),
            score_threshold=self.score_threshold,
            preserve_cross_document_duplicates=True,
        )
        hits_by_session = {
            session_number: [
                hit
                for hit in reranked
                if hit.chunk.session_number == session_number
            ]
            for session_number in session_numbers
        }

        selected: list[SearchHit] = []
        selected_chunk_ids: set[str] = set()
        for evidence_index in range(self.minimum_session_evidence):
            for session_number in session_numbers:
                session_hits = hits_by_session[session_number]
                if evidence_index >= len(session_hits):
                    continue
                hit = session_hits[evidence_index]
                if hit.chunk.chunk_id in selected_chunk_ids:
                    continue
                selected.append(hit)
                selected_chunk_ids.add(hit.chunk.chunk_id)
                if len(selected) >= request.top_k:
                    return self._with_ranks(selected)

        for hit in reranked:
            if hit.chunk.chunk_id in selected_chunk_ids:
                continue
            selected.append(hit)
            selected_chunk_ids.add(hit.chunk.chunk_id)
            if len(selected) >= request.top_k:
                break
        return self._with_ranks(selected)

    @staticmethod
    def _with_ranks(hits: list[SearchHit]) -> list[SearchHit]:
        return [
            hit.model_copy(update={"rank": rank})
            for rank, hit in enumerate(hits, start=1)
        ]
