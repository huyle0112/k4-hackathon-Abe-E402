from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from app.rag.models import Chunk, SearchHit


class VectorStoreError(RuntimeError):
    """Raised when the local vector store cannot satisfy an operation."""


class ChromaVectorStore:
    def __init__(
        self,
        *,
        path: str | Path,
        collection_name: str,
        embedding_provider_name: str,
        embedding_dimension: int,
    ) -> None:
        try:
            import chromadb
        except ImportError as error:
            raise VectorStoreError(
                "ChromaDB is required. Install backend requirements first."
            ) from error

        self.path = Path(path).resolve()
        self.path.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.embedding_provider_name = embedding_provider_name
        self.embedding_dimension = embedding_dimension
        self._client = chromadb.PersistentClient(path=str(self.path))
        self._collection = self._get_or_create_collection()
        self._validate_collection()

    def _get_or_create_collection(self) -> Any:
        return self._client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=None,
            metadata={
                "hnsw:space": "cosine",
                "embedding_provider": self.embedding_provider_name,
                "embedding_dimension": self.embedding_dimension,
            },
        )

    def _validate_collection(self) -> None:
        metadata = self._collection.metadata or {}
        existing_dimension = metadata.get("embedding_dimension")
        existing_provider = metadata.get("embedding_provider")
        if self._collection.count() == 0:
            return
        if existing_dimension and int(existing_dimension) != self.embedding_dimension:
            raise VectorStoreError(
                "Embedding dimension differs from the existing collection. "
                "Use a new collection or rebuild the local vector store."
            )
        if existing_provider and existing_provider != self.embedding_provider_name:
            raise VectorStoreError(
                "Embedding provider differs from the existing collection. "
                "Use a new collection or rebuild the local vector store."
            )

    def count(self) -> int:
        return int(self._collection.count())

    def upsert(
        self,
        chunks: Sequence[Chunk],
        embeddings: Sequence[Sequence[float]],
        *,
        batch_size: int = 100,
    ) -> int:
        if len(chunks) != len(embeddings):
            raise VectorStoreError("Chunks and embeddings must have equal length")
        if not chunks:
            return 0

        for start in range(0, len(chunks), batch_size):
            batch_chunks = chunks[start : start + batch_size]
            batch_embeddings = embeddings[start : start + batch_size]
            self._collection.upsert(
                ids=[chunk.chunk_id for chunk in batch_chunks],
                embeddings=[list(vector) for vector in batch_embeddings],
                documents=[chunk.text for chunk in batch_chunks],
                metadatas=[
                    self._chunk_to_metadata(chunk) for chunk in batch_chunks
                ],
            )
        return len(chunks)

    def delete_stale_chunks(
        self, document_id: str, current_chunk_ids: set[str]
    ) -> int:
        existing = self._collection.get(
            where={"document_id": document_id},
            include=[],
        )
        existing_ids = set(existing.get("ids") or [])
        stale_ids = sorted(existing_ids - current_chunk_ids)
        if stale_ids:
            self._collection.delete(ids=stale_ids)
        return len(stale_ids)

    def query(
        self,
        query_embedding: Sequence[float],
        *,
        n_results: int,
        where: dict[str, Any] | None = None,
    ) -> list[SearchHit]:
        if self.count() == 0:
            return []

        result = self._collection.query(
            query_embeddings=[list(query_embedding)],
            n_results=min(max(1, n_results), self.count()),
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        ids = (result.get("ids") or [[]])[0]
        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]

        hits: list[SearchHit] = []
        for rank, (chunk_id, text, metadata, distance) in enumerate(
            zip(ids, documents, metadatas, distances, strict=False),
            start=1,
        ):
            if text is None or metadata is None:
                continue
            score = max(-1.0, min(1.0, 1.0 - float(distance)))
            chunk = self._metadata_to_chunk(chunk_id, text, metadata)
            hits.append(
                SearchHit(
                    chunk=chunk,
                    score=score,
                    vector_score=score,
                    rank=rank,
                )
            )
        return hits

    def reset(self) -> None:
        try:
            self._client.delete_collection(self.collection_name)
        except Exception:
            pass
        self._collection = self._get_or_create_collection()

    @staticmethod
    def _chunk_to_metadata(chunk: Chunk) -> dict[str, Any]:
        return {
            "document_id": chunk.document_id,
            "document_title": chunk.document_title,
            "session_number": chunk.session_number,
            "source_file": chunk.source_file,
            "slide_number": chunk.slide_number,
            "chunk_index": chunk.chunk_index,
            "extraction_method": chunk.extraction_method,
            "content_hash": chunk.content_hash,
            "token_count": chunk.token_count,
        }

    @staticmethod
    def _metadata_to_chunk(
        chunk_id: str, text: str, metadata: dict[str, Any]
    ) -> Chunk:
        return Chunk(
            chunk_id=chunk_id,
            document_id=str(metadata["document_id"]),
            document_title=str(metadata["document_title"]),
            session_number=int(metadata["session_number"]),
            source_file=str(metadata["source_file"]),
            slide_number=int(metadata["slide_number"]),
            chunk_index=int(metadata["chunk_index"]),
            text=text,
            extraction_method=str(metadata["extraction_method"]),
            content_hash=str(metadata["content_hash"]),
            token_count=int(metadata["token_count"]),
        )
