from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from app.config import Settings
from app.rag.generation.citations import citations_belong_to_hits
from app.rag.generation.generator import (
    AnswerGenerator,
    LLMConfigurationError,
    LLMProviderError,
    OpenAITextGenerationProvider,
    StaticTextGenerationProvider,
    create_text_generation_provider,
)
from app.rag.models import Chunk, LLMAnswer, SearchHit


class FakeResponsesAPI:
    def __init__(
        self,
        *,
        response: Any | None = None,
        error: Exception | None = None,
    ) -> None:
        self.response = response
        self.error = error
        self.calls: list[dict[str, Any]] = []

    def parse(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.response


class FakeOpenAIClient:
    def __init__(
        self,
        *,
        response: Any | None = None,
        error: Exception | None = None,
    ) -> None:
        self.responses = FakeResponsesAPI(
            response=response,
            error=error,
        )


def _settings(tmp_path: Path, **overrides: Any) -> Settings:
    values: dict[str, Any] = {
        "repo_root": tmp_path,
        "lessons_dir": tmp_path / "lessons",
        "vector_store_dir": tmp_path / "chroma",
    }
    values.update(overrides)
    return Settings(**values)


def _response(
    *,
    cited_chunk_ids: list[str],
    answer: str = "Câu trả lời có kiểm chứng.",
    abstained: bool = False,
    reason: str | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        status="completed",
        output=[],
        output_parsed=LLMAnswer(
            answer=answer,
            abstained=abstained,
            reason=reason,
            cited_chunk_ids=cited_chunk_ids,
        ),
        usage=SimpleNamespace(
            input_tokens=100,
            output_tokens=20,
            total_tokens=120,
        ),
        _request_id="req_test",
    )


def _hit(
    score: float = 0.8,
    *,
    session: int = 1,
) -> SearchHit:
    text = (
        "Context là lượng nội dung mô hình có thể nhìn thấy khi trả lời."
        if session == 1
        else "Reward function giúp đánh giá kết quả của hệ thống AI."
    )
    chunk = Chunk(
        chunk_id=f"day-{session:02d}-slide-14-chunk-01",
        document_id=f"day-{session:02d}",
        document_title=f"Day {session}",
        session_number=session,
        source_file=f"day-{session:02d}.pdf",
        slide_number=14,
        chunk_index=1,
        text=text,
        extraction_method="text",
        content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        token_count=len(text.split()),
    )
    return SearchHit(
        chunk=chunk,
        score=score,
        vector_score=score,
        lexical_score=0.8,
        rank=1,
    )


def test_extractive_generation_includes_valid_citation() -> None:
    hit = _hit()

    result = AnswerGenerator().generate("Context là gì?", [hit])

    assert not result.abstained
    assert result.citations[0].slide_number == 14
    assert citations_belong_to_hits(result.citations, [hit])
    assert "slide 14" in result.answer


def test_generation_abstains_without_sources() -> None:
    result = AnswerGenerator().generate("Câu hỏi ngoài phạm vi", [])

    assert result.abstained
    assert result.confidence == 0.0
    assert result.citations == []


def test_generation_abstains_when_evidence_coverage_is_low() -> None:
    weak_hit = _hit(score=0.2).model_copy(
        update={"vector_score": 0.2, "lexical_score": 0.1}
    )

    result = AnswerGenerator().generate(
        "Công thức nấu món ăn ngoài phạm vi?", [weak_hit]
    )

    assert result.abstained
    assert result.citations == []


def test_static_provider_can_replace_extractive_fallback() -> None:
    provider = StaticTextGenerationProvider("Câu trả lời kiểm thử.")

    result = AnswerGenerator(provider=provider).generate(
        "Context là gì?", [_hit()]
    )

    assert result.answer == "Câu trả lời kiểm thử."
    assert not result.abstained


def test_blank_llm_configuration_keeps_extractive_fallback(
    tmp_path: Path,
) -> None:
    settings = _settings(
        tmp_path,
        llm_provider=None,
        llm_model=None,
        llm_api_key=None,
    )

    assert create_text_generation_provider(settings) is None


def test_blank_llm_environment_values_normalize_to_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LLM_PROVIDER", " ")
    monkeypatch.setenv("LLM_MODEL", "")
    monkeypatch.setenv("LLM_API_KEY", " ")
    monkeypatch.setenv("LLM_BASE_URL", "")
    monkeypatch.setenv("LLM_REASONING_EFFORT", " ")

    settings = Settings.from_env()

    assert settings.llm_provider is None
    assert settings.llm_model is None
    assert settings.llm_api_key is None
    assert settings.llm_base_url is None
    assert settings.llm_reasoning_effort is None


@pytest.mark.parametrize(
    ("model", "api_key", "expected_variable"),
    [
        (None, "test-placeholder", "LLM_MODEL"),
        ("test-model", None, "LLM_API_KEY"),
    ],
)
def test_openai_provider_fails_fast_when_configuration_is_missing(
    tmp_path: Path,
    model: str | None,
    api_key: str | None,
    expected_variable: str,
) -> None:
    settings = _settings(
        tmp_path,
        llm_provider="openai",
        llm_model=model,
        llm_api_key=api_key,
    )

    with pytest.raises(LLMConfigurationError, match=expected_variable):
        create_text_generation_provider(settings)


def test_llm_api_key_is_hidden_from_settings_repr(tmp_path: Path) -> None:
    settings = _settings(
        tmp_path,
        llm_api_key="test-secret-placeholder",
    )

    assert "test-secret-placeholder" not in repr(settings)


def test_openai_responses_api_uses_structured_output_and_no_storage() -> None:
    hit = _hit()
    client = FakeOpenAIClient(
        response=_response(cited_chunk_ids=[hit.chunk.chunk_id])
    )
    provider = OpenAITextGenerationProvider(
        api_key="test-placeholder",
        model_name="test-model",
        reasoning_effort="medium",
        client=client,
    )

    generated = provider.generate_structured(
        instructions="System rule only.",
        query="Context là gì?",
        evidence_context='[{"chunk_id":"allowed"}]',
    )

    assert generated.output.answer == "Câu trả lời có kiểm chứng."
    assert generated.metadata.request_id == "req_test"
    assert generated.metadata.usage is not None
    assert generated.metadata.usage.total_tokens == 120
    call = client.responses.calls[0]
    assert call["store"] is False
    assert call["tools"] == []
    assert call["text_format"] is LLMAnswer
    assert call["instructions"] == "System rule only."
    assert "System rule only." not in str(call["input"])
    assert "Context là gì?" in call["input"][0]["content"]
    assert "chunk_id" in call["input"][1]["content"]
    assert call["reasoning"] == {"effort": "medium"}


def test_openai_provider_configures_finite_retry_and_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_openai(**kwargs: Any) -> FakeOpenAIClient:
        captured.update(kwargs)
        return FakeOpenAIClient()

    monkeypatch.setattr("openai.OpenAI", fake_openai)

    OpenAITextGenerationProvider(
        api_key="test-placeholder",
        model_name="test-model",
        base_url="https://example.invalid/v1",
        timeout_seconds=12.5,
        max_retries=2,
    )

    assert captured == {
        "api_key": "test-placeholder",
        "timeout": 12.5,
        "max_retries": 2,
        "base_url": "https://example.invalid/v1",
    }


def test_invalid_and_duplicate_citations_are_filtered() -> None:
    hit = _hit()
    provider = OpenAITextGenerationProvider(
        api_key="test-placeholder",
        model_name="test-model",
        client=FakeOpenAIClient(
            response=_response(
                cited_chunk_ids=[
                    hit.chunk.chunk_id,
                    "invented-chunk",
                    hit.chunk.chunk_id,
                ]
            )
        ),
    )

    result = AnswerGenerator(provider=provider).generate(
        "Context là gì?",
        [hit],
    )

    assert not result.abstained
    assert [citation.chunk_id for citation in result.citations] == [
        hit.chunk.chunk_id
    ]
    assert result.citations[0].source_file == hit.chunk.source_file
    assert result.citations[0].slide_number == hit.chunk.slide_number
    assert result.confidence < 0.8


def test_cross_session_answer_requires_citations_from_each_session() -> None:
    first = _hit(session=1)
    second = _hit(session=2)
    provider = OpenAITextGenerationProvider(
        api_key="test-placeholder",
        model_name="test-model",
        client=FakeOpenAIClient(
            response=_response(
                cited_chunk_ids=[first.chunk.chunk_id]
            )
        ),
    )

    result = AnswerGenerator(provider=provider).generate(
        "Liên hệ hai buổi",
        [first, second],
        required_session_numbers=[1, 2],
    )

    assert result.abstained
    assert result.citations == []
    assert "chưa trích dẫn đủ" in (result.reason or "")


def test_cross_session_answer_accepts_valid_citations_from_each_session() -> None:
    first = _hit(session=1)
    second = _hit(session=2)
    provider = OpenAITextGenerationProvider(
        api_key="test-placeholder",
        model_name="test-model",
        client=FakeOpenAIClient(
            response=_response(
                cited_chunk_ids=[
                    first.chunk.chunk_id,
                    second.chunk.chunk_id,
                ]
            )
        ),
    )

    result = AnswerGenerator(provider=provider).generate(
        "Liên hệ hai buổi",
        [first, second],
        required_session_numbers=[1, 2],
    )

    assert not result.abstained
    assert {
        citation.document_id for citation in result.citations
    } == {"day-01", "day-02"}


def test_missing_cross_session_evidence_forces_abstention() -> None:
    result = AnswerGenerator().generate(
        "Liên hệ hai buổi",
        [_hit(session=1)],
        required_session_numbers=[1, 2],
    )

    assert result.abstained
    assert result.citations == []
    assert "Thiếu evidence" in (result.reason or "")


@pytest.mark.parametrize(
    ("response", "expected_kind"),
    [
        (
            SimpleNamespace(
                status="incomplete",
                incomplete_details=SimpleNamespace(
                    reason="max_output_tokens"
                ),
                output=[],
                output_parsed=None,
                usage=None,
            ),
            "incomplete_max_output_tokens",
        ),
        (
            SimpleNamespace(
                status="incomplete",
                incomplete_details=SimpleNamespace(
                    reason="content_filter"
                ),
                output=[],
                output_parsed=None,
                usage=None,
            ),
            "incomplete_content_filter",
        ),
        (
            SimpleNamespace(
                status="completed",
                output=[
                    SimpleNamespace(
                        content=[
                            SimpleNamespace(type="refusal")
                        ]
                    )
                ],
                output_parsed=None,
                usage=None,
            ),
            "refusal",
        ),
    ],
)
def test_incomplete_and_refusal_responses_are_rejected(
    response: SimpleNamespace,
    expected_kind: str,
) -> None:
    provider = OpenAITextGenerationProvider(
        api_key="test-placeholder",
        model_name="test-model",
        client=FakeOpenAIClient(response=response),
    )

    with pytest.raises(LLMProviderError) as raised:
        provider.generate_structured(
            instructions="rule",
            query="query",
            evidence_context="[]",
        )

    assert raised.value.kind == expected_kind


@pytest.mark.parametrize(
    ("error_type", "expected_kind"),
    [
        ("APITimeoutError", "timeout"),
        ("RateLimitError", "rate_limit"),
        ("AuthenticationError", "authentication"),
        ("BadRequestError", "validation"),
    ],
)
def test_provider_errors_are_sanitized_without_manual_retry(
    error_type: str,
    expected_kind: str,
) -> None:
    error_class = type(error_type, (Exception,), {})
    client = FakeOpenAIClient(error=error_class("private error details"))
    provider = OpenAITextGenerationProvider(
        api_key="test-placeholder",
        model_name="test-model",
        client=client,
    )

    with pytest.raises(LLMProviderError) as raised:
        provider.generate_structured(
            instructions="rule",
            query="query",
            evidence_context="[]",
        )

    assert raised.value.kind == expected_kind
    assert len(client.responses.calls) == 1
    assert "private error details" not in str(raised.value)


def test_timeout_returns_controlled_abstention_not_extractive_answer() -> None:
    timeout_class = type("APITimeoutError", (Exception,), {})
    provider = OpenAITextGenerationProvider(
        api_key="test-placeholder",
        model_name="test-model",
        client=FakeOpenAIClient(
            error=timeout_class("private timeout details")
        ),
    )

    result = AnswerGenerator(provider=provider).generate(
        "Context là gì?",
        [_hit()],
    )

    assert result.abstained
    assert result.citations == []
    assert result.generation is not None
    assert result.generation.error_type == "timeout"
    assert "Theo các slide" not in result.answer

from app.rag.generation.generator import generate_answer
from app.rag.models import Chunk, SearchHit


def test_generation_abstains_when_confidence_is_low():
    chunk = Chunk(id="x", text="Một đoạn nội dung bài giảng đủ dài để làm nguồn.", file_name="a.pdf", session_id="d1", page=3)
    response = generate_answer("câu hỏi", [SearchHit(chunk=chunk, score=0.01)], 0.12)
    assert response.status == "low_confidence"
    assert response.citations[0].page == 3
