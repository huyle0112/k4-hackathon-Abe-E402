import math
import re
import unicodedata
from collections import Counter

TOKEN_RE = re.compile(r"\b\w{2,}\b", re.UNICODE)


def tokenize(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return TOKEN_RE.findall(normalized)


def embed(text: str) -> dict[str, float]:
    counts = Counter(tokenize(text))
    norm = math.sqrt(sum(value * value for value in counts.values()))
    if not norm:
        return {}
    return {token: count / norm for token, count in counts.items()}


def cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    if len(left) > len(right):
        left, right = right, left
    return max(0.0, min(1.0, sum(value * right.get(token, 0.0) for token, value in left.items())))

from __future__ import annotations

import hashlib
import math
import re
import unicodedata
from collections.abc import Sequence
from typing import Any, Protocol

from app.config import Settings


_WORD = re.compile(r"\w+", re.UNICODE)


class EmbeddingConfigurationError(ValueError):
    """Raised when an embedding provider is configured incompletely."""


class EmbeddingProviderError(RuntimeError):
    """Raised when an embedding provider returns an invalid result."""


class EmbeddingProvider(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def model_name(self) -> str: ...

    @property
    def dimension(self) -> int: ...

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class HashEmbeddingProvider:
    """Deterministic local baseline requiring no model download or API key."""

    def __init__(self, dimension: int = 384) -> None:
        if dimension < 64:
            raise ValueError("Embedding dimension must be at least 64")
        self._dimension = dimension

    @property
    def name(self) -> str:
        return f"hash-ngram-{self._dimension}"

    @property
    def model_name(self) -> str:
        return "hash-ngram"

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        normalized = unicodedata.normalize("NFC", text).lower()
        words = _WORD.findall(normalized)
        compact = " ".join(words)
        features: list[str] = []

        features.extend(f"w:{word}" for word in words)
        features.extend(
            f"b:{words[index]}_{words[index + 1]}"
            for index in range(len(words) - 1)
        )
        padded = f"  {compact}  "
        for size in (3, 4, 5):
            features.extend(
                f"c:{padded[index:index + size]}"
                for index in range(max(0, len(padded) - size + 1))
            )

        vector = [0.0] * self._dimension
        for feature in features:
            digest = hashlib.blake2b(
                feature.encode("utf-8"), digest_size=8
            ).digest()
            index = int.from_bytes(digest[:4], "little") % self._dimension
            sign = 1.0 if digest[4] & 1 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


class SentenceTransformerEmbeddingProvider:
    """Optional multilingual local embedding adapter."""

    def __init__(self, model_name: str) -> None:
        if not model_name:
            raise ValueError("A local sentence-transformer model is required")
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as error:
            raise RuntimeError(
                "Install sentence-transformers to use the local model provider"
            ) from error

        self._model_name = model_name
        self._model = SentenceTransformer(model_name)
        dimension = self._model.get_sentence_embedding_dimension()
        if dimension is None:
            raise RuntimeError("Cannot determine embedding dimension")
        self._dimension = int(dimension)

    @property
    def name(self) -> str:
        return f"sentence-transformers:{self._model_name}"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        embeddings = self._model.encode(
            list(texts),
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


class OpenAIEmbeddingProvider:
    """Semantic embedding provider backed by the OpenAI embeddings API."""

    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        dimension: int,
        batch_size: int = 64,
        timeout_seconds: float = 60.0,
        max_retries: int = 3,
        base_url: str = "",
        client: Any | None = None,
    ) -> None:
        if not api_key.strip():
            raise EmbeddingConfigurationError(
                "EMBEDDING_API_KEY is required when "
                "EMBEDDING_PROVIDER=openai."
            )
        if not model_name.strip():
            raise EmbeddingConfigurationError(
                "EMBEDDING_MODEL is required when "
                "EMBEDDING_PROVIDER=openai."
            )
        if dimension < 1:
            raise EmbeddingConfigurationError(
                "EMBEDDING_DIMENSION must be positive."
            )
        if batch_size < 1:
            raise EmbeddingConfigurationError(
                "EMBEDDING_BATCH_SIZE must be positive."
            )
        if timeout_seconds <= 0:
            raise EmbeddingConfigurationError(
                "EMBEDDING_TIMEOUT_SECONDS must be positive."
            )
        if max_retries < 0:
            raise EmbeddingConfigurationError(
                "EMBEDDING_MAX_RETRIES cannot be negative."
            )

        self._model_name = model_name.strip()
        self._dimension = dimension
        self._batch_size = batch_size
        if client is None:
            try:
                from openai import OpenAI
            except ImportError as error:
                raise EmbeddingConfigurationError(
                    "Install the OpenAI SDK from backend requirements."
                ) from error

            client_options: dict[str, Any] = {
                "api_key": api_key,
                "timeout": timeout_seconds,
                "max_retries": max_retries,
            }
            if base_url.strip():
                client_options["base_url"] = base_url.strip()
            client = OpenAI(**client_options)
        self._client = client

    @property
    def name(self) -> str:
        return f"openai:{self._model_name}:{self._dimension}"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        normalized_texts = [str(text) for text in texts]
        if not normalized_texts:
            return []

        embeddings: list[list[float]] = []
        for start in range(0, len(normalized_texts), self._batch_size):
            batch = normalized_texts[start : start + self._batch_size]
            embeddings.extend(self._embed_batch(batch))
        return embeddings

    def embed_query(self, text: str) -> list[float]:
        return self._embed_batch([text])[0]

    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        try:
            response = self._client.embeddings.create(
                input=texts,
                model=self._model_name,
                dimensions=self._dimension,
                encoding_format="float",
            )
        except Exception as error:
            raise EmbeddingProviderError(
                "OpenAI embeddings request failed "
                f"({type(error).__name__})."
            ) from error

        data = list(getattr(response, "data", []))
        if len(data) != len(texts):
            raise EmbeddingProviderError(
                "OpenAI embeddings response count does not match input count."
            )

        try:
            ordered = sorted(data, key=lambda item: int(item.index))
            indexes = [int(item.index) for item in ordered]
        except (AttributeError, TypeError, ValueError) as error:
            raise EmbeddingProviderError(
                "OpenAI embeddings response is missing valid indexes."
            ) from error
        if indexes != list(range(len(texts))):
            raise EmbeddingProviderError(
                "OpenAI embeddings response indexes are invalid."
            )

        vectors: list[list[float]] = []
        for item in ordered:
            vector = [float(value) for value in item.embedding]
            if len(vector) != self._dimension:
                raise EmbeddingProviderError(
                    "OpenAI embedding dimension does not match "
                    "EMBEDDING_DIMENSION."
                )
            vectors.append(vector)
        return vectors


def create_embedding_provider(
    settings: Settings,
    *,
    client: Any | None = None,
) -> EmbeddingProvider:
    provider = settings.embedding_provider.strip().lower()
    if provider == "hash":
        return HashEmbeddingProvider(settings.embedding_dimension)
    if provider in {"sentence-transformers", "sentence_transformers", "local"}:
        return SentenceTransformerEmbeddingProvider(
            settings.local_embedding_model
        )
    if provider in {"openai", "openai-compatible", "openai_compatible"}:
        return OpenAIEmbeddingProvider(
            api_key=settings.embedding_api_key,
            model_name=settings.embedding_model,
            dimension=settings.embedding_dimension,
            batch_size=settings.embedding_batch_size,
            timeout_seconds=settings.embedding_timeout_seconds,
            max_retries=settings.embedding_max_retries,
            base_url=settings.embedding_base_url,
            client=client,
        )
    raise ValueError(f"Unsupported embedding provider: {provider}")
