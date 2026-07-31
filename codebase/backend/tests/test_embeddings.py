from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from app.config import Settings
from app.rag.embeddings import (
    EmbeddingConfigurationError,
    EmbeddingProviderError,
    HashEmbeddingProvider,
    OpenAIEmbeddingProvider,
    create_embedding_provider,
)
from app.rag.models import Chunk
from app.rag.vector_store import ChromaVectorStore, VectorStoreError


class FakeEmbeddingsAPI:
    def __init__(self, *, wrong_dimension: bool = False) -> None:
        self.calls: list[dict[str, Any]] = []
        self.wrong_dimension = wrong_dimension

    def create(self, **kwargs: Any) -> SimpleNamespace:
        self.calls.append(kwargs)
        dimension = int(kwargs["dimensions"])
        if self.wrong_dimension:
            dimension -= 1
        data = [
            SimpleNamespace(
                index=index,
                embedding=[float(index + 1)] * dimension,
            )
            for index, _ in enumerate(kwargs["input"])
        ]
        return SimpleNamespace(data=list(reversed(data)))


class FakeOpenAIClient:
    def __init__(self, *, wrong_dimension: bool = False) -> None:
        self.embeddings = FakeEmbeddingsAPI(
            wrong_dimension=wrong_dimension
        )


def _settings(tmp_path: Path, **overrides: Any) -> Settings:
    values: dict[str, Any] = {
        "repo_root": tmp_path,
        "lessons_dir": tmp_path / "lessons",
        "vector_store_dir": tmp_path / "chroma",
    }
    values.update(overrides)
    return Settings(**values)


def _chunk() -> Chunk:
    text = "Nội dung semantic embedding giả dùng cho kiểm thử."
    return Chunk(
        chunk_id="day-01-slide-01-chunk-01",
        document_id="day-01",
        document_title="Day 1",
        session_number=1,
        source_file="day-01.pdf",
        slide_number=1,
        chunk_index=1,
        text=text,
        extraction_method="text",
        content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        token_count=len(text.split()),
    )


def test_blank_environment_values_use_safe_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LESSONS_DIR", " ")
    monkeypatch.setenv("VECTOR_STORE_DIR", "")
    monkeypatch.setenv("EMBEDDING_PROVIDER", "")
    monkeypatch.setenv("EMBEDDING_DIMENSION", "")

    settings = Settings.from_env()

    assert settings.embedding_provider == "hash"
    assert settings.embedding_dimension == 384
    assert settings.lessons_dir.name == "lessons"
    assert settings.vector_store_dir.name == "chroma"


def test_embedding_api_key_is_hidden_from_settings_repr(
    tmp_path: Path,
) -> None:
    settings = _settings(
        tmp_path,
        embedding_api_key="test-secret-placeholder",
    )

    assert "test-secret-placeholder" not in repr(settings)


def test_openai_provider_requires_api_key(tmp_path: Path) -> None:
    settings = _settings(
        tmp_path,
        embedding_provider="openai",
        embedding_model="text-embedding-3-large",
        embedding_api_key="",
        embedding_dimension=3072,
    )

    with pytest.raises(
        EmbeddingConfigurationError,
        match="EMBEDDING_API_KEY",
    ):
        create_embedding_provider(settings)


def test_explicit_hash_provider_remains_available(tmp_path: Path) -> None:
    provider = create_embedding_provider(
        _settings(
            tmp_path,
            embedding_provider="hash",
            embedding_dimension=128,
        )
    )

    assert isinstance(provider, HashEmbeddingProvider)
    assert provider.dimension == 128


def test_openai_provider_batches_and_preserves_order() -> None:
    client = FakeOpenAIClient()
    provider = OpenAIEmbeddingProvider(
        api_key="test-placeholder",
        model_name="text-embedding-3-large",
        dimension=4,
        batch_size=2,
        client=client,
    )

    vectors = provider.embed_documents(["a", "b", "c", "d", "e"])

    assert len(client.embeddings.calls) == 3
    assert [len(call["input"]) for call in client.embeddings.calls] == [
        2,
        2,
        1,
    ]
    assert all(
        call["model"] == "text-embedding-3-large"
        and call["dimensions"] == 4
        and call["encoding_format"] == "float"
        for call in client.embeddings.calls
    )
    assert vectors[0] == [1.0] * 4
    assert vectors[1] == [2.0] * 4
    assert len(vectors) == 5


def test_openai_provider_configures_finite_retry_and_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_openai(**kwargs: Any) -> FakeOpenAIClient:
        captured.update(kwargs)
        return FakeOpenAIClient()

    monkeypatch.setattr("openai.OpenAI", fake_openai)

    OpenAIEmbeddingProvider(
        api_key="test-placeholder",
        model_name="text-embedding-3-large",
        dimension=4,
        timeout_seconds=12.5,
        max_retries=2,
        base_url="https://example.invalid/v1",
    )

    assert captured == {
        "api_key": "test-placeholder",
        "timeout": 12.5,
        "max_retries": 2,
        "base_url": "https://example.invalid/v1",
    }


def test_openai_provider_rejects_wrong_dimension() -> None:
    provider = OpenAIEmbeddingProvider(
        api_key="test-placeholder",
        model_name="text-embedding-3-large",
        dimension=4,
        client=FakeOpenAIClient(wrong_dimension=True),
    )

    with pytest.raises(EmbeddingProviderError, match="dimension"):
        provider.embed_query("Câu hỏi giả")


def test_vector_store_rejects_model_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "chroma"
    first = ChromaVectorStore(
        path=path,
        collection_name="model_mismatch",
        embedding_provider_name="openai",
        embedding_model_name="model-a",
        embedding_dimension=3,
    )
    first.upsert([_chunk()], [[1.0, 0.0, 0.0]])

    with pytest.raises(VectorStoreError, match="model differs"):
        ChromaVectorStore(
            path=path,
            collection_name="model_mismatch",
            embedding_provider_name="openai",
            embedding_model_name="model-b",
            embedding_dimension=3,
        )


def test_vector_store_rejects_dimension_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "chroma"
    first = ChromaVectorStore(
        path=path,
        collection_name="dimension_mismatch",
        embedding_provider_name="openai",
        embedding_model_name="model-a",
        embedding_dimension=3,
    )
    first.upsert([_chunk()], [[1.0, 0.0, 0.0]])

    with pytest.raises(VectorStoreError, match="dimension differs"):
        ChromaVectorStore(
            path=path,
            collection_name="dimension_mismatch",
            embedding_provider_name="openai",
            embedding_model_name="model-a",
            embedding_dimension=4,
        )


def test_explicit_rebuild_allows_embedding_migration(
    tmp_path: Path,
) -> None:
    path = tmp_path / "chroma"
    original = ChromaVectorStore(
        path=path,
        collection_name="migration",
        embedding_provider_name="hash-ngram-3",
        embedding_model_name="hash-ngram",
        embedding_dimension=3,
    )
    original.upsert([_chunk()], [[1.0, 0.0, 0.0]])

    migrated = ChromaVectorStore(
        path=path,
        collection_name="migration",
        embedding_provider_name="openai:text-embedding-3-large:4",
        embedding_model_name="text-embedding-3-large",
        embedding_dimension=4,
        allow_incompatible=True,
    )
    migrated.reset()

    assert migrated.count() == 0
    assert migrated.embedding_metadata() == {
        "embedding_provider": "openai:text-embedding-3-large:4",
        "embedding_model": "text-embedding-3-large",
        "embedding_dimension": 4,
    }
