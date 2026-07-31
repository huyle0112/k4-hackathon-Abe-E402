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
