from typing import Literal

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    id: str
    text: str
    file_name: str
    session_id: str
    page: int = Field(ge=1)
    slide: int | None = Field(default=None, ge=1)
    embedding: dict[str, float] = Field(default_factory=dict)


class SearchHit(BaseModel):
    chunk: Chunk
    score: float = Field(ge=0, le=1)


class Citation(BaseModel):
    file_name: str
    session_id: str
    page: int
    slide: int | None = None
    excerpt: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    session_ids: list[str] = Field(default_factory=list)
    file_names: list[str] = Field(default_factory=list)
    top_k: int | None = Field(default=None, ge=1, le=20)


class ChatResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)
    status: Literal["answered", "low_confidence", "no_context"]
    citations: list[Citation] = Field(default_factory=list)
