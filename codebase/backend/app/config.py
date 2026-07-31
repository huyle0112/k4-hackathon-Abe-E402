from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    repo_root: Path
    lessons_dir: Path
    vector_store_dir: Path
    collection_name: str = "ai_in_action_lessons"
    embedding_provider: str = "hash"
    embedding_dimension: int = 384
    local_embedding_model: str = ""
    chunk_max_tokens: int = 700
    chunk_overlap_tokens: int = 80
    retrieval_top_k: int = 5
    retrieval_candidate_k: int = 20
    retrieval_score_threshold: float = 0.12
    retrieval_min_lexical_coverage: float = 0.4
    retrieval_min_vector_score: float = 0.28
    ocr_enabled: bool = True
    ocr_languages: str = "vie+eng"
    ocr_dpi: int = 240

    @classmethod
    def from_env(cls) -> "Settings":
        backend_root = Path(__file__).resolve().parents[1]
        repo_root = backend_root.parent.parent
        lessons_dir = Path(
            os.getenv("LESSONS_DIR", str(repo_root / "private-data" / "lessons"))
        ).resolve()
        vector_store_dir = Path(
            os.getenv(
                "VECTOR_STORE_DIR",
                str(repo_root / "vector-store" / "chroma"),
            )
        ).resolve()

        return cls(
            repo_root=repo_root,
            lessons_dir=lessons_dir,
            vector_store_dir=vector_store_dir,
            collection_name=os.getenv(
                "COLLECTION_NAME", "ai_in_action_lessons"
            ),
            embedding_provider=os.getenv("EMBEDDING_PROVIDER", "hash"),
            embedding_dimension=int(os.getenv("EMBEDDING_DIMENSION", "384")),
            local_embedding_model=os.getenv("LOCAL_EMBEDDING_MODEL", ""),
            chunk_max_tokens=int(os.getenv("CHUNK_MAX_TOKENS", "700")),
            chunk_overlap_tokens=int(
                os.getenv("CHUNK_OVERLAP_TOKENS", "80")
            ),
            retrieval_top_k=int(os.getenv("RETRIEVAL_TOP_K", "5")),
            retrieval_candidate_k=int(
                os.getenv("RETRIEVAL_CANDIDATE_K", "20")
            ),
            retrieval_score_threshold=float(
                os.getenv("RETRIEVAL_SCORE_THRESHOLD", "0.12")
            ),
            retrieval_min_lexical_coverage=float(
                os.getenv("RETRIEVAL_MIN_LEXICAL_COVERAGE", "0.4")
            ),
            retrieval_min_vector_score=float(
                os.getenv("RETRIEVAL_MIN_VECTOR_SCORE", "0.28")
            ),
            ocr_enabled=_as_bool(os.getenv("OCR_ENABLED"), True),
            ocr_languages=os.getenv("OCR_LANGUAGES", "vie+eng"),
            ocr_dpi=int(os.getenv("OCR_DPI", "240")),
        )
