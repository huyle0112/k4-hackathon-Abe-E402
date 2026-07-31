from __future__ import annotations
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VLearn Cross-session Tutor"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    vector_store_path: Path = Path("vector-store/chunks.json")
    top_k: int = 5
    confidence_threshold: float = 0.12

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

import os
from dataclasses import dataclass, field
from pathlib import Path


def _env_text(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip()
    return normalized if normalized else default


def _env_optional_text(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _env_int(name: str, default: int) -> int:
    value = _env_text(name)
    return int(value) if value else default


def _env_float(name: str, default: float) -> float:
    value = _env_text(name)
    return float(value) if value else default


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None or not value.strip():
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    repo_root: Path
    lessons_dir: Path
    vector_store_dir: Path
    app_name: str = "VLearn Cross-session Tutor"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    collection_name: str = "ai_in_action_lessons"
    embedding_provider: str = "hash"
    embedding_model: str = ""
    embedding_api_key: str = field(default="", repr=False)
    embedding_base_url: str = ""
    embedding_dimension: int = 384
    embedding_batch_size: int = 64
    embedding_timeout_seconds: float = 60.0
    embedding_max_retries: int = 3
    local_embedding_model: str = ""
    llm_provider: str | None = None
    llm_model: str | None = None
    llm_api_key: str | None = field(default=None, repr=False)
    llm_base_url: str | None = None
    llm_reasoning_effort: str | None = None
    llm_max_output_tokens: int = 1200
    llm_timeout_seconds: float = 60.0
    llm_max_retries: int = 2
    chunk_max_tokens: int = 700
    chunk_overlap_tokens: int = 80
    retrieval_top_k: int = 5
    retrieval_candidate_k: int = 20
    retrieval_min_session_evidence: int = 1
    retrieval_score_threshold: float = 0.12
    retrieval_min_lexical_coverage: float = 0.4
    retrieval_min_vector_score: float = 0.28
    generation_max_context_chunks: int = 8
    generation_max_context_tokens: int = 3500
    ocr_enabled: bool = True
    ocr_languages: str = "vie+eng"
    ocr_dpi: int = 240

    @classmethod
    def from_env(cls) -> "Settings":
        backend_root = Path(__file__).resolve().parents[1]
        repo_root = backend_root.parent.parent
        lessons_dir = Path(
            _env_text(
                "LESSONS_DIR",
                str(repo_root / "private-data" / "lessons"),
            )
        ).resolve()
        vector_store_dir = Path(
            _env_text(
                "VECTOR_STORE_DIR",
                str(repo_root / "vector-store" / "chroma"),
            )
        ).resolve()

        return cls(
            repo_root=repo_root,
            lessons_dir=lessons_dir,
            vector_store_dir=vector_store_dir,
            collection_name=_env_text(
                "COLLECTION_NAME", "ai_in_action_lessons"
            ),
            embedding_provider=_env_text("EMBEDDING_PROVIDER", "hash"),
            embedding_model=_env_text("EMBEDDING_MODEL"),
            embedding_api_key=_env_text("EMBEDDING_API_KEY"),
            embedding_base_url=_env_text("EMBEDDING_BASE_URL"),
            embedding_dimension=_env_int("EMBEDDING_DIMENSION", 384),
            embedding_batch_size=_env_int("EMBEDDING_BATCH_SIZE", 64),
            embedding_timeout_seconds=_env_float(
                "EMBEDDING_TIMEOUT_SECONDS", 60.0
            ),
            embedding_max_retries=_env_int("EMBEDDING_MAX_RETRIES", 3),
            local_embedding_model=_env_text("LOCAL_EMBEDDING_MODEL"),
            llm_provider=_env_optional_text("LLM_PROVIDER"),
            llm_model=_env_optional_text("LLM_MODEL"),
            llm_api_key=_env_optional_text("LLM_API_KEY"),
            llm_base_url=_env_optional_text("LLM_BASE_URL"),
            llm_reasoning_effort=_env_optional_text(
                "LLM_REASONING_EFFORT"
            ),
            llm_max_output_tokens=_env_int(
                "LLM_MAX_OUTPUT_TOKENS", 1200
            ),
            llm_timeout_seconds=_env_float(
                "LLM_TIMEOUT_SECONDS", 60.0
            ),
            llm_max_retries=_env_int("LLM_MAX_RETRIES", 2),
            chunk_max_tokens=_env_int("CHUNK_MAX_TOKENS", 700),
            chunk_overlap_tokens=_env_int("CHUNK_OVERLAP_TOKENS", 80),
            retrieval_top_k=_env_int("RETRIEVAL_TOP_K", 5),
            retrieval_candidate_k=_env_int(
                "RETRIEVAL_CANDIDATE_K", 20
            ),
            retrieval_min_session_evidence=_env_int(
                "RETRIEVAL_MIN_SESSION_EVIDENCE", 1
            ),
            retrieval_score_threshold=_env_float(
                "RETRIEVAL_SCORE_THRESHOLD", 0.12
            ),
            retrieval_min_lexical_coverage=_env_float(
                "RETRIEVAL_MIN_LEXICAL_COVERAGE", 0.4
            ),
            retrieval_min_vector_score=_env_float(
                "RETRIEVAL_MIN_VECTOR_SCORE", 0.28
            ),
            generation_max_context_chunks=_env_int(
                "GENERATION_MAX_CONTEXT_CHUNKS", 8
            ),
            generation_max_context_tokens=_env_int(
                "GENERATION_MAX_CONTEXT_TOKENS", 3500
            ),
            ocr_enabled=_as_bool(os.getenv("OCR_ENABLED"), True),
            ocr_languages=_env_text("OCR_LANGUAGES", "vie+eng"),
            ocr_dpi=_env_int("OCR_DPI", 240),
        )

    @property
    def allowed_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

from functools import lru_cache

@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
