from __future__ import annotations
import json
from pathlib import Path
from threading import RLock

from app.rag.embeddings import cosine_similarity, embed
from app.rag.models import Chunk, SearchHit


class JsonVectorStore:
    def __init__(self, path: Path):
        self.path = path
        self._lock = RLock()
        self._chunks: list[Chunk] = []
        self.load()

    def load(self) -> None:
        with self._lock:
            if self.path.exists():
                payload = json.loads(self.path.read_text(encoding="utf-8"))
                self._chunks = [Chunk.model_validate(item) for item in payload]

    def save(self) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            data = [chunk.model_dump(mode="json") for chunk in self._chunks]
            self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def replace_session(self, session_id: str, chunks: list[Chunk]) -> int:
        with self._lock:
            self._chunks = [item for item in self._chunks if item.session_id != session_id] + chunks
            self.save()
            return len(chunks)

    def search(
        self,
        query: str,
        top_k: int,
        session_ids: list[str] | None = None,
        file_names: list[str] | None = None,
    ) -> list[SearchHit]:
        query_embedding = embed(query)
        sessions = set(session_ids or [])
        files = set(file_names or [])
        candidates = (
            chunk for chunk in self._chunks
            if (not sessions or chunk.session_id in sessions)
            and (not files or chunk.file_name in files)
        )
        hits = [
            SearchHit(chunk=chunk, score=cosine_similarity(query_embedding, chunk.embedding))
            for chunk in candidates
        ]
        return sorted(hits, key=lambda hit: hit.score, reverse=True)[:top_k]

    @property
    def count(self) -> int:
        return len(self._chunks)


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
        embedding_model_name: str = "",
        allow_incompatible: bool = False,
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
        self.embedding_model_name = embedding_model_name
        self.embedding_dimension = embedding_dimension
        self.allow_incompatible = allow_incompatible
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
                "embedding_model": self.embedding_model_name,
                "embedding_dimension": self.embedding_dimension,
            },
        )

    def _validate_collection(self) -> None:
        metadata = self._collection.metadata or {}
        existing_dimension = metadata.get("embedding_dimension")
        existing_provider = metadata.get("embedding_provider")
        existing_model = metadata.get("embedding_model")
        if self._collection.count() == 0:
            return
        mismatches: list[str] = []
        if (
            existing_dimension
            and int(existing_dimension) != self.embedding_dimension
        ):
            mismatches.append("dimension")
        if (
            existing_provider
            and existing_provider != self.embedding_provider_name
        ):
            mismatches.append("provider")
        if (
            existing_model
            and self.embedding_model_name
            and existing_model != self.embedding_model_name
        ):
            mismatches.append("model")
        if not mismatches:
            return
        if self.allow_incompatible:
            return
        if "dimension" in mismatches:
            raise VectorStoreError(
                "Embedding dimension differs from the existing collection. "
                "Run ingestion with --rebuild or use a new collection."
            )
        if "provider" in mismatches:
            raise VectorStoreError(
                "Embedding provider differs from the existing collection. "
                "Run ingestion with --rebuild or use a new collection."
            )
        raise VectorStoreError(
            "Embedding model differs from the existing collection. "
            "Run ingestion with --rebuild or use a new collection."
        )

    def embedding_metadata(self) -> dict[str, Any]:
        metadata = self._collection.metadata or {}
        return {
            "embedding_provider": metadata.get("embedding_provider"),
            "embedding_model": metadata.get("embedding_model"),
            "embedding_dimension": metadata.get("embedding_dimension"),
        }

    def _validate_embedding(self, embedding: Sequence[float]) -> None:
        if len(embedding) != self.embedding_dimension:
            raise VectorStoreError(
                "Embedding vector dimension does not match the collection "
                f"dimension ({self.embedding_dimension})."
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
        for embedding in embeddings:
            self._validate_embedding(embedding)

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
        self._validate_embedding(query_embedding)

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

    def get_chunks(
        self, *, where: dict[str, Any] | None = None
    ) -> list[Chunk]:
        result = self._collection.get(
            where=where,
            include=["documents", "metadatas"],
        )
        chunks = [
            self._metadata_to_chunk(chunk_id, text, metadata)
            for chunk_id, text, metadata in zip(
                result.get("ids") or [],
                result.get("documents") or [],
                result.get("metadatas") or [],
                strict=False,
            )
            if text is not None and metadata is not None
        ]
        return sorted(
            chunks,
            key=lambda item: (
                item.session_number,
                item.slide_number,
                item.chunk_index,
            ),
        )

    def reset(self) -> None:
        self._client.delete_collection(self.collection_name)
        self._collection = self._get_or_create_collection()
        self.allow_incompatible = False
        self._validate_collection()

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
