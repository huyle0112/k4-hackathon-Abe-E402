from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


ExtractionMethod = Literal["text", "ocr", "none"]


class DocumentMetadata(BaseModel):
    document_id: str
    document_title: str
    session_number: int = Field(ge=1)
    source_file: str
    total_pages: int = Field(ge=1)
    file_sha256: str


class PageContent(BaseModel):
    document_id: str
    page_number: int = Field(ge=1)
    text: str
    extraction_method: ExtractionMethod
    char_count: int = Field(ge=0)
    warnings: list[str] = Field(default_factory=list)


class LoadedDocument(BaseModel):
    metadata: DocumentMetadata
    pages: list[PageContent]

    @field_validator("pages")
    @classmethod
    def page_numbers_must_be_unique(
        cls, pages: list[PageContent]
    ) -> list[PageContent]:
        numbers = [page.page_number for page in pages]
        if len(numbers) != len(set(numbers)):
            raise ValueError("Page numbers must be unique")
        return pages


class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    session_number: int = Field(ge=1)
    source_file: str
    slide_number: int = Field(ge=1)
    chunk_index: int = Field(ge=1)
    text: str = Field(min_length=1)
    extraction_method: ExtractionMethod
    content_hash: str
    token_count: int = Field(ge=1)


class RetrievalRequest(BaseModel):
    query: str = Field(min_length=1)
    session_numbers: list[int] | None = None
    top_k: int = Field(default=5, ge=1, le=50)

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Query must not be blank")
        return normalized

    @field_validator("session_numbers")
    @classmethod
    def sessions_must_be_positive_and_unique(
        cls, value: list[int] | None
    ) -> list[int] | None:
        if value is None:
            return None
        if any(number < 1 for number in value):
            raise ValueError("Session numbers must be positive")
        return sorted(set(value))


class SearchHit(BaseModel):
    chunk: Chunk
    score: float
    rank: int = Field(ge=1)
    vector_score: float | None = None
    lexical_score: float | None = None


class Citation(BaseModel):
    source_file: str
    document_id: str
    document_title: str
    slide_number: int = Field(ge=1)
    chunk_id: str
    excerpt: str


class GenerationResult(BaseModel):
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    abstained: bool
    citations: list[Citation] = Field(default_factory=list)
    reason: str | None = None


class ChatResponse(GenerationResult):
    retrieval_hits: list[SearchHit] = Field(default_factory=list)


class DocumentIngestionResult(BaseModel):
    document_id: str
    source_file: str
    total_pages: int
    text_pages: int
    ocr_pages: int
    empty_pages: int
    chunk_count: int
    indexed_count: int
    warnings: list[str] = Field(default_factory=list)


class IngestionReport(BaseModel):
    source_directory: str
    dry_run: bool
    documents: list[DocumentIngestionResult]

    @property
    def total_pages(self) -> int:
        return sum(document.total_pages for document in self.documents)

    @property
    def total_chunks(self) -> int:
        return sum(document.chunk_count for document in self.documents)


class ExpectedSource(BaseModel):
    document_id: str
    slide_number: int = Field(ge=1)


class GoldenCase(BaseModel):
    case_id: str = Field(min_length=1)
    category: Literal[
        "single-session",
        "cross-session",
        "low-confidence",
        "out-of-scope",
        "correction",
    ]
    query: str = Field(min_length=1)
    session_numbers: list[int] | None = None
    expected_abstain: bool
    expected_sources: list[ExpectedSource] = Field(default_factory=list)
    expected_answer_notes: str | None = None


class EvaluationCaseResult(BaseModel):
    case_id: str
    category: str
    passed: bool
    abstention_correct: bool
    retrieval_hit: bool | None
    citation_hit: bool | None


class EvaluationReport(BaseModel):
    case_count: int
    pass_rate: float
    abstention_accuracy: float
    retrieval_hit_rate: float | None
    citation_hit_rate: float | None
    cases: list[EvaluationCaseResult]
