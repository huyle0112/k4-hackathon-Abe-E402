from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Any, Protocol

from app.config import Settings

from app.rag.generation.citations import (
    build_citations,
    build_citations_for_chunk_ids,
    citations_belong_to_hits,
)
from app.rag.generation.prompt import (
    SYSTEM_INSTRUCTION,
    build_evidence_context,
    build_generation_prompt,
)
from app.rag.models import (
    GenerationMetadata,
    GenerationResult,
    GenerationUsage,
    LLMAnswer,
    SearchHit,
)


class LLMConfigurationError(ValueError):
    """Raised when a selected LLM provider is configured incompletely."""


class LLMProviderError(RuntimeError):
    """Sanitized provider failure safe to expose through an abstention."""

    def __init__(
        self,
        kind: str,
        *,
        metadata: GenerationMetadata | None = None,
    ) -> None:
        super().__init__(f"LLM provider failed ({kind}).")
        self.kind = kind
        self.metadata = metadata


class TextGenerationProvider(Protocol):
    @property
    def name(self) -> str: ...

    def generate(self, prompt: str) -> str: ...


class StructuredTextGenerationProvider(Protocol):
    @property
    def name(self) -> str: ...

    def generate_structured(
        self,
        *,
        instructions: str,
        query: str,
        evidence_context: str,
    ) -> "ProviderGenerationResult": ...


@dataclass(frozen=True)
class ProviderGenerationResult:
    output: LLMAnswer
    metadata: GenerationMetadata


class StaticTextGenerationProvider:
    """Deterministic provider for tests and integration development."""

    def __init__(self, response: str) -> None:
        self.response = response

    @property
    def name(self) -> str:
        return "static"

    def generate(self, prompt: str) -> str:
        del prompt
        return self.response


class OpenAITextGenerationProvider:
    """Structured text generation through the OpenAI Responses API."""

    def __init__(
        self,
        *,
        api_key: str | None,
        model_name: str | None,
        base_url: str | None = None,
        reasoning_effort: str | None = None,
        max_output_tokens: int = 1200,
        timeout_seconds: float = 60.0,
        max_retries: int = 2,
        client: Any | None = None,
    ) -> None:
        if not api_key or not api_key.strip():
            raise LLMConfigurationError(
                "LLM_API_KEY is required when LLM_PROVIDER=openai."
            )
        if not model_name or not model_name.strip():
            raise LLMConfigurationError(
                "LLM_MODEL is required when LLM_PROVIDER=openai."
            )
        if max_output_tokens < 1:
            raise LLMConfigurationError(
                "LLM_MAX_OUTPUT_TOKENS must be positive."
            )
        if timeout_seconds <= 0:
            raise LLMConfigurationError(
                "LLM_TIMEOUT_SECONDS must be positive."
            )
        if max_retries < 0:
            raise LLMConfigurationError(
                "LLM_MAX_RETRIES cannot be negative."
            )

        self._model_name = model_name.strip()
        self._reasoning_effort = (
            reasoning_effort.strip()
            if reasoning_effort and reasoning_effort.strip()
            else None
        )
        self._max_output_tokens = max_output_tokens
        if client is None:
            try:
                from openai import OpenAI
            except ImportError as error:
                raise LLMConfigurationError(
                    "Install the OpenAI SDK from backend requirements."
                ) from error

            client_options: dict[str, Any] = {
                "api_key": api_key,
                "timeout": timeout_seconds,
                "max_retries": max_retries,
            }
            if base_url and base_url.strip():
                client_options["base_url"] = base_url.strip()
            client = OpenAI(**client_options)
        self._client = client

    @property
    def name(self) -> str:
        return f"openai:{self._model_name}"

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate_structured(
        self,
        *,
        instructions: str,
        query: str,
        evidence_context: str,
    ) -> ProviderGenerationResult:
        request: dict[str, Any] = {
            "model": self._model_name,
            "instructions": instructions,
            "input": [
                {
                    "role": "user",
                    "content": f"CÂU HỎI:\n{query}",
                },
                {
                    "role": "user",
                    "content": (
                        "EVIDENCE KHÔNG ĐÁNG TIN CẬY (JSON):\n"
                        f"{evidence_context}"
                    ),
                },
            ],
            "text_format": LLMAnswer,
            "store": False,
            "tools": [],
            "max_output_tokens": self._max_output_tokens,
        }
        if self._reasoning_effort:
            request["reasoning"] = {"effort": self._reasoning_effort}

        started_at = time.perf_counter()
        try:
            response = self._client.responses.parse(**request)
        except Exception as error:
            latency_ms = (time.perf_counter() - started_at) * 1000
            kind = self._classify_error(error)
            raise LLMProviderError(
                kind,
                metadata=GenerationMetadata(
                    mode="openai",
                    provider="openai",
                    model=self._model_name,
                    latency_ms=latency_ms,
                    error_type=kind,
                ),
            ) from error

        latency_ms = (time.perf_counter() - started_at) * 1000
        metadata = self._build_metadata(response, latency_ms=latency_ms)
        status = str(self._read_value(response, "status") or "")
        if status == "incomplete":
            details = self._read_value(response, "incomplete_details")
            reason = str(self._read_value(details, "reason") or "unknown")
            kind = f"incomplete_{reason}"
            raise LLMProviderError(
                kind,
                metadata=metadata.model_copy(
                    update={"error_type": kind}
                ),
            )
        if status and status != "completed":
            kind = f"response_{status}"
            raise LLMProviderError(
                kind,
                metadata=metadata.model_copy(
                    update={"error_type": kind}
                ),
            )
        if self._contains_refusal(response):
            raise LLMProviderError(
                "refusal",
                metadata=metadata.model_copy(
                    update={"error_type": "refusal"}
                ),
            )

        parsed = self._read_value(response, "output_parsed")
        if parsed is None:
            raise LLMProviderError(
                "missing_structured_output",
                metadata=metadata.model_copy(
                    update={"error_type": "missing_structured_output"}
                ),
            )
        try:
            output = LLMAnswer.model_validate(parsed)
        except Exception as error:
            raise LLMProviderError(
                "invalid_structured_output",
                metadata=metadata.model_copy(
                    update={"error_type": "invalid_structured_output"}
                ),
            ) from error
        return ProviderGenerationResult(output=output, metadata=metadata)

    def _build_metadata(
        self,
        response: Any,
        *,
        latency_ms: float,
    ) -> GenerationMetadata:
        usage_value = self._read_value(response, "usage")
        usage = None
        if usage_value is not None:
            usage = GenerationUsage(
                input_tokens=self._optional_int(
                    self._read_value(usage_value, "input_tokens")
                ),
                output_tokens=self._optional_int(
                    self._read_value(usage_value, "output_tokens")
                ),
                total_tokens=self._optional_int(
                    self._read_value(usage_value, "total_tokens")
                ),
            )
        return GenerationMetadata(
            mode="openai",
            provider="openai",
            model=self._model_name,
            latency_ms=latency_ms,
            response_status=str(
                self._read_value(response, "status") or ""
            )
            or None,
            request_id=str(
                self._read_value(response, "_request_id")
                or self._read_value(response, "request_id")
                or ""
            )
            or None,
            usage=usage,
        )

    @classmethod
    def _contains_refusal(cls, response: Any) -> bool:
        for item in cls._read_value(response, "output") or []:
            for content in cls._read_value(item, "content") or []:
                if cls._read_value(content, "type") == "refusal":
                    return True
        return False

    @staticmethod
    def _read_value(value: Any, name: str) -> Any:
        if value is None:
            return None
        if isinstance(value, dict):
            return value.get(name)
        return getattr(value, name, None)

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        return int(value) if value is not None else None

    @staticmethod
    def _classify_error(error: Exception) -> str:
        error_name = type(error).__name__.lower()
        if "lengthfinishreason" in error_name:
            return "incomplete_max_output_tokens"
        if "contentfilterfinishreason" in error_name:
            return "incomplete_content_filter"
        if "timeout" in error_name:
            return "timeout"
        if "ratelimit" in error_name or "rate_limit" in error_name:
            return "rate_limit"
        if "authentication" in error_name:
            return "authentication"
        if "permission" in error_name:
            return "permission"
        if (
            "badrequest" in error_name
            or "validation" in error_name
            or "unprocessable" in error_name
        ):
            return "validation"
        if "connection" in error_name:
            return "connection"
        return "provider_error"


def create_text_generation_provider(
    settings: Settings,
    *,
    client: Any | None = None,
) -> OpenAITextGenerationProvider | None:
    provider = (settings.llm_provider or "").strip().lower()
    model = (settings.llm_model or "").strip()
    if not provider and not model:
        return None
    if not provider:
        raise LLMConfigurationError(
            "LLM_PROVIDER is required when LLM_MODEL is configured."
        )
    if provider != "openai":
        raise LLMConfigurationError(
            f"Unsupported LLM provider: {provider}"
        )
    return OpenAITextGenerationProvider(
        api_key=settings.llm_api_key,
        model_name=settings.llm_model,
        base_url=settings.llm_base_url,
        reasoning_effort=settings.llm_reasoning_effort,
        max_output_tokens=settings.llm_max_output_tokens,
        timeout_seconds=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
        client=client,
    )


class AnswerGenerator:
    def __init__(
        self,
        *,
        provider: TextGenerationProvider | None = None,
        abstention_threshold: float = 0.12,
        minimum_lexical_coverage: float = 0.4,
        minimum_vector_score: float = 0.28,
        maximum_citations: int = 5,
        maximum_context_chunks: int = 8,
        maximum_context_tokens: int = 3500,
        minimum_session_evidence: int = 1,
    ) -> None:
        if maximum_context_chunks < 1:
            raise ValueError("maximum_context_chunks must be positive")
        if maximum_context_tokens < 1:
            raise ValueError("maximum_context_tokens must be positive")
        if minimum_session_evidence < 1:
            raise ValueError("minimum_session_evidence must be positive")
        self.provider = provider
        self.abstention_threshold = abstention_threshold
        self.minimum_lexical_coverage = minimum_lexical_coverage
        self.minimum_vector_score = minimum_vector_score
        self.maximum_citations = maximum_citations
        self.maximum_context_chunks = maximum_context_chunks
        self.maximum_context_tokens = maximum_context_tokens
        self.minimum_session_evidence = minimum_session_evidence

    def generate(
        self,
        query: str,
        hits: list[SearchHit],
        *,
        required_session_numbers: list[int] | None = None,
        trusted_context: bool = False,
    ) -> GenerationResult:
        if not hits:
            return self._abstain("Không tìm thấy nguồn liên quan.")

        confidence = self._confidence(hits)
        required_sessions = sorted(set(required_session_numbers or []))
        if len(required_sessions) >= 2 and not self._sessions_have_coverage(
            hits,
            required_sessions,
        ):
            return self._abstain(
                "Thiếu evidence phù hợp từ ít nhất một buổi được yêu cầu.",
                confidence=confidence,
            )
        if not trusted_context and hits[0].score < self.abstention_threshold:
            return self._abstain(
                "Nguồn tìm được chưa đạt ngưỡng liên quan.",
                confidence=confidence,
            )
        top_lexical = hits[0].lexical_score or 0.0
        top_vector = hits[0].vector_score or 0.0
        if not trusted_context and (
            top_lexical < self.minimum_lexical_coverage
            and top_vector < self.minimum_vector_score
        ):
            return self._abstain(
                "Nguồn không bao phủ đủ các khái niệm chính trong câu hỏi.",
                confidence=confidence,
            )

        context_hits = (
            hits
            if trusted_context
            else self._select_context_hits(
                hits,
                required_sessions=required_sessions,
            )
        )
        if not context_hits:
            return self._abstain(
                "Không có evidence nào phù hợp với giới hạn context.",
                confidence=confidence,
            )
        if len(required_sessions) >= 2 and not self._sessions_have_coverage(
            context_hits,
            required_sessions,
        ):
            return self._abstain(
                "Giới hạn context không giữ đủ nguồn từ các buổi yêu cầu.",
                confidence=confidence,
            )

        structured_method = getattr(
            self.provider,
            "generate_structured",
            None,
        )
        if callable(structured_method):
            return self._generate_structured(
                query,
                context_hits,
                confidence=confidence,
                required_sessions=required_sessions,
            )

        citations = build_citations(
            context_hits,
            maximum_citations=self.maximum_citations,
        )
        if not citations or not citations_belong_to_hits(
            citations,
            context_hits,
        ):
            return self._abstain(
                "Không thể tạo citation hợp lệ.",
                confidence=confidence,
            )

        if self.provider is not None:
            answer = self.provider.generate(
                build_generation_prompt(query, context_hits)
            ).strip()
            generation = GenerationMetadata(
                mode="static",
                provider=self.provider.name,
            )
        else:
            answer = self._extractive_answer(context_hits)
            generation = GenerationMetadata(mode="extractive")

        if not answer:
            return self._abstain(
                "Không thể tạo câu trả lời từ nguồn hiện có.",
                confidence=confidence,
            )

        return GenerationResult(
            answer=answer,
            confidence=confidence,
            abstained=False,
            citations=citations,
            generation=generation,
        )

    def _generate_structured(
        self,
        query: str,
        context_hits: list[SearchHit],
        *,
        confidence: float,
        required_sessions: list[int],
    ) -> GenerationResult:
        if self.provider is None:
            return self._abstain(
                "LLM provider chưa được khởi tạo.",
                confidence=confidence,
            )
        try:
            generated = self.provider.generate_structured(
                instructions=SYSTEM_INSTRUCTION,
                query=query,
                evidence_context=build_evidence_context(context_hits),
            )
        except LLMProviderError as error:
            return self._abstain(
                self._provider_failure_reason(error.kind),
                confidence=confidence,
                generation=error.metadata,
            )

        output = generated.output
        if output.abstained:
            return self._abstain(
                output.reason or "LLM xác định evidence chưa đủ.",
                confidence=confidence,
                generation=generated.metadata,
            )
        answer = output.answer.strip()
        if not answer:
            return self._abstain(
                "LLM không trả về nội dung câu trả lời.",
                confidence=confidence,
                generation=generated.metadata,
            )

        proposed_ids = list(dict.fromkeys(output.cited_chunk_ids))
        citations = build_citations_for_chunk_ids(
            context_hits,
            proposed_ids,
            maximum_citations=self.maximum_citations,
        )
        if not citations or not citations_belong_to_hits(
            citations,
            context_hits,
        ):
            return self._abstain(
                "LLM không cung cấp citation hợp lệ cho câu trả lời.",
                confidence=confidence,
                generation=generated.metadata,
            )
        if len(required_sessions) >= 2:
            cited_sessions = {
                hit.chunk.session_number
                for hit in context_hits
                if any(
                    citation.chunk_id == hit.chunk.chunk_id
                    for citation in citations
                )
            }
            if not set(required_sessions).issubset(cited_sessions):
                return self._abstain(
                    "Câu trả lời chưa trích dẫn đủ các buổi được yêu cầu.",
                    confidence=confidence,
                    generation=generated.metadata,
                )

        if proposed_ids:
            valid_ratio = len(citations) / len(proposed_ids)
            confidence = round(confidence * valid_ratio, 4)
        return GenerationResult(
            answer=answer,
            confidence=confidence,
            abstained=False,
            citations=citations,
            reason=output.reason,
            generation=generated.metadata,
        )

    def _select_context_hits(
        self,
        hits: list[SearchHit],
        *,
        required_sessions: list[int],
    ) -> list[SearchHit]:
        selected: list[SearchHit] = []
        selected_ids: set[str] = set()
        used_tokens = 0

        def add_if_fits(hit: SearchHit) -> bool:
            nonlocal used_tokens
            if hit.chunk.chunk_id in selected_ids:
                return False
            if len(selected) >= self.maximum_context_chunks:
                return False
            if used_tokens + hit.chunk.token_count > self.maximum_context_tokens:
                return False
            selected.append(hit)
            selected_ids.add(hit.chunk.chunk_id)
            used_tokens += hit.chunk.token_count
            return True

        if len(required_sessions) >= 2:
            for evidence_index in range(self.minimum_session_evidence):
                for session_number in required_sessions:
                    session_hits = [
                        hit
                        for hit in hits
                        if hit.chunk.session_number == session_number
                    ]
                    if evidence_index < len(session_hits):
                        add_if_fits(session_hits[evidence_index])

        for hit in hits:
            add_if_fits(hit)
        return selected

    def _sessions_have_coverage(
        self,
        hits: list[SearchHit],
        required_sessions: list[int],
    ) -> bool:
        counts = {
            session_number: sum(
                hit.chunk.session_number == session_number
                for hit in hits
            )
            for session_number in required_sessions
        }
        return all(
            count >= self.minimum_session_evidence
            for count in counts.values()
        )

    @staticmethod
    def _provider_failure_reason(kind: str) -> str:
        reasons = {
            "timeout": "LLM hết thời gian chờ; hệ thống không tự thay câu trả lời.",
            "rate_limit": "LLM đang giới hạn lưu lượng; vui lòng thử lại sau.",
            "authentication": "Cấu hình xác thực LLM không hợp lệ.",
            "permission": "API key không có quyền dùng model LLM đã chọn.",
            "validation": "Yêu cầu LLM không hợp lệ với model đã chọn.",
            "refusal": "LLM từ chối tạo câu trả lời.",
            "incomplete_max_output_tokens": (
                "LLM dừng vì đạt giới hạn output token."
            ),
            "incomplete_content_filter": (
                "LLM dừng vì bộ lọc nội dung."
            ),
            "missing_structured_output": (
                "LLM không trả về structured output."
            ),
            "invalid_structured_output": (
                "Structured output của LLM không hợp lệ."
            ),
        }
        return reasons.get(
            kind,
            "Không thể tạo câu trả lời bằng LLM ở thời điểm hiện tại.",
        )

    @staticmethod
    def _confidence(hits: list[SearchHit]) -> float:
        scores = [max(0.0, min(1.0, hit.score)) for hit in hits[:3]]
        top_score = scores[0]
        mean_score = sum(scores) / len(scores)
        unique_documents = len(
            {hit.chunk.document_id for hit in hits[:3]}
        )
        source_support = min(1.0, unique_documents / 2)
        margin = (
            max(0.0, top_score - scores[1]) if len(scores) > 1 else top_score
        )
        heuristic = (
            top_score * 0.55
            + mean_score * 0.25
            + source_support * 0.10
            + min(1.0, margin * 2) * 0.10
        )
        return round(max(0.0, min(1.0, heuristic)), 4)

    @staticmethod
    def _extractive_answer(hits: list[SearchHit]) -> str:
        statements: list[str] = []
        for hit in hits[:3]:
            compact = re.sub(r"\s+", " ", hit.chunk.text).strip()
            sentences = re.split(r"(?<=[.!?])\s+", compact)
            excerpt = " ".join(sentences[:2]).strip()
            if len(excerpt) > 500:
                excerpt = f"{excerpt[:497].rsplit(' ', 1)[0]}…"
            if excerpt:
                statements.append(
                    f"- {excerpt} "
                    f"[{hit.chunk.source_file}, slide "
                    f"{hit.chunk.slide_number}]"
                )
        if not statements:
            return ""
        return "Theo các slide được truy xuất:\n\n" + "\n".join(statements)

    @staticmethod
    def _abstain(
        reason: str,
        *,
        confidence: float = 0.0,
        generation: GenerationMetadata | None = None,
    ) -> GenerationResult:
        return GenerationResult(
            answer=(
                "Mình không đủ căn cứ trong tài liệu để trả lời câu hỏi này."
            ),
            confidence=confidence,
            abstained=True,
            citations=[],
            reason=reason,
            generation=generation,
        )

import re

from app.rag.generation.citations import build_citations
from app.rag.models import ChatResponse, SearchHit


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", text) if len(part.strip()) > 20]


def generate_answer(question: str, hits: list[SearchHit], threshold: float) -> ChatResponse:
    if not hits:
        return ChatResponse(
            answer="Chưa có nội dung bài giảng phù hợp trong phạm vi đã chọn.",
            confidence=0,
            status="no_context",
        )
    confidence = round(hits[0].score, 3)
    if confidence < threshold:
        return ChatResponse(
            answer="Mình chưa tìm thấy căn cứ đủ chắc chắn trong các bài đã chọn. Hãy chọn thêm buổi học hoặc đặt câu hỏi cụ thể hơn.",
            confidence=confidence,
            status="low_confidence",
            citations=build_citations(hits[:1]),
        )
    selected: list[str] = []
    for hit in hits[:3]:
        sentences = _sentences(hit.chunk.text)
        selected.append(sentences[0] if sentences else hit.chunk.text[:300])
    answer = "Dựa trên các bài giảng đã chọn:\n\n" + "\n".join(f"- {text}" for text in selected)
    return ChatResponse(
        answer=answer,
        confidence=confidence,
        status="answered",
        citations=build_citations(hits),
    )
