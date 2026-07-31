from __future__ import annotations

import hashlib
import math
import re
import unicodedata
from collections.abc import Sequence
from typing import Protocol, Any

from app.config import Settings


_WORD = re.compile(r"\w+", re.UNICODE)


class EmbeddingProvider(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def model(self) -> str: ...

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
    def model(self) -> str:
        return "hash"

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
    def model(self) -> str:
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
    """Uses OpenAI API to generate semantic embeddings."""

    def __init__(
        self,
        api_key: str,
        model: str,
        dimension: int,
        base_url: str | None = None,
        batch_size: int = 64,
        timeout: int = 60,
        max_retries: int = 3,
        client_factory: Any = None,
    ) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("OpenAI API key is required but missing or empty. Please set EMBEDDING_API_KEY.")
        if not model or not model.strip():
            raise ValueError("OpenAI embedding model name is required but missing or empty. Please set EMBEDDING_MODEL.")
        
        try:
            import openai
        except ImportError as error:
            raise RuntimeError(
                "Install openai package to use OpenAIEmbeddingProvider (e.g. pip install openai)"
            ) from error

        self._model = model.strip()
        self._dimension = dimension
        self._batch_size = max(1, batch_size)
        
        if client_factory:
            self._client = client_factory()
        else:
            base_url_val = base_url.strip() if base_url and base_url.strip() else None
            self._client = openai.Client(
                api_key=api_key.strip(),
                base_url=base_url_val,
                timeout=timeout,
                max_retries=max_retries,
            )

    @property
    def name(self) -> str:
        return "openai"

    @property
    def model(self) -> str:
        return self._model

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        texts = list(texts)
        if not texts:
            return []
            
        all_embeddings = []
        for start in range(0, len(texts), self._batch_size):
            batch = texts[start : start + self._batch_size]
            response = self._client.embeddings.create(
                input=batch,
                model=self._model,
                dimensions=self._dimension
            )
            for data in response.data:
                all_embeddings.append(data.embedding)
        return all_embeddings

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


def create_embedding_provider(settings: Settings) -> EmbeddingProvider:
    provider = settings.embedding_provider.strip().lower()
    if provider == "hash":
        return HashEmbeddingProvider(settings.embedding_dimension)
    if provider in {"sentence-transformers", "sentence_transformers", "local"}:
        return SentenceTransformerEmbeddingProvider(
            settings.local_embedding_model
        )
    if provider == "openai":
        return OpenAIEmbeddingProvider(
            api_key=settings.embedding_api_key,
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
            base_url=settings.embedding_base_url,
            batch_size=settings.embedding_batch_size,
            timeout=settings.embedding_timeout_seconds,
            max_retries=settings.embedding_max_retries,
        )
    raise ValueError(f"Unsupported embedding provider: {provider}")
