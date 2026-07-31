from __future__ import annotations

import hashlib
from pathlib import Path

from app.rag.embeddings import HashEmbeddingProvider
from app.rag.models import Chunk, RetrievalRequest
from app.rag.retrieval.reranker import BaselineReranker
from app.rag.retrieval.retriever import Retriever
from app.rag.vector_store import ChromaVectorStore


def _chunk(
    chunk_id: str,
    *,
    session: int,
    slide: int,
    text: str,
) -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        document_id=f"day-{session:02d}",
        document_title=f"Day {session}",
        session_number=session,
        source_file=f"day-{session:02d}.pdf",
        slide_number=slide,
        chunk_index=1,
        text=text,
        extraction_method="text",
        content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        token_count=len(text.split()),
    )


def _build_retriever(tmp_path: Path) -> tuple[Retriever, ChromaVectorStore]:
    chunks = [
        _chunk(
            "day-01-slide-01-chunk-01",
            session=1,
            slide=1,
            text="Context là lượng thông tin mô hình nhìn thấy khi trả lời.",
        ),
        _chunk(
            "day-01-slide-02-chunk-01",
            session=1,
            slide=2,
            text="Attention giúp mô hình chú ý đến các token liên quan.",
        ),
        _chunk(
            "day-02-slide-01-chunk-01",
            session=2,
            slide=1,
            text="Reward function xác định kết quả đúng hoặc sai.",
        ),
    ]
    embedding = HashEmbeddingProvider(128)
    store = ChromaVectorStore(
        path=tmp_path / "chroma",
        collection_name="test_retrieval",
        embedding_provider_name=embedding.name,
        embedding_dimension=embedding.dimension,
    )
    store.upsert(
        chunks,
        embedding.embed_documents([chunk.text for chunk in chunks]),
    )
    retriever = Retriever(
        embedding_provider=embedding,
        vector_store=store,
        reranker=BaselineReranker(),
        candidate_k=10,
        score_threshold=0.0,
    )
    return retriever, store


def test_retrieval_finds_relevant_slide(tmp_path: Path) -> None:
    retriever, _ = _build_retriever(tmp_path)

    hits = retriever.retrieve(
        RetrievalRequest(query="Context của mô hình là gì?", top_k=2)
    )

    assert hits
    assert hits[0].chunk.chunk_id == "day-01-slide-01-chunk-01"
    assert hits[0].rank == 1


def test_retrieval_filters_sessions(tmp_path: Path) -> None:
    retriever, _ = _build_retriever(tmp_path)

    hits = retriever.retrieve(
        RetrievalRequest(
            query="Kết quả đúng sai được xác định thế nào?",
            session_numbers=[2],
            top_k=3,
        )
    )

    assert hits
    assert all(hit.chunk.session_number == 2 for hit in hits)


def test_cross_session_retrieval_preserves_each_requested_session(
    tmp_path: Path,
) -> None:
    retriever, _ = _build_retriever(tmp_path)

    hits = retriever.retrieve(
        RetrievalRequest(
            query="Context và reward function liên hệ thế nào?",
            session_numbers=[1, 2],
            top_k=2,
        )
    )

    assert len(hits) == 2
    assert {hit.chunk.session_number for hit in hits} == {1, 2}
    assert [hit.rank for hit in hits] == [1, 2]


def test_unfiltered_retrieval_does_not_force_cross_session_coverage(
    tmp_path: Path,
) -> None:
    retriever, _ = _build_retriever(tmp_path)

    hits = retriever.retrieve(
        RetrievalRequest(
            query="Context của mô hình là gì?",
            top_k=1,
        )
    )

    assert len(hits) == 1
    assert hits[0].chunk.session_number == 1


def test_vector_store_deletes_only_stale_chunks(tmp_path: Path) -> None:
    _, store = _build_retriever(tmp_path)

    deleted = store.delete_stale_chunks(
        "day-01", {"day-01-slide-01-chunk-01"}
    )

    assert deleted == 1
    assert store.count() == 2
