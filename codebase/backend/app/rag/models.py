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


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    text: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    course_code: str
    slide_id: str | None = None
    page: int | None = None
    history: list[HistoryMessage] | None = None
    top_k: int | None = Field(default=None, ge=1, le=20)


class ChatResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)
    status: Literal["answered", "low_confidence", "no_context"]
    citations: list[Citation] = Field(default_factory=list)


class SlideFile(BaseModel):
    id: str
    day: int
    file_name: str
    url: str
    label: str
    pdf_path: str = ""


class CourseDay(BaseModel):
    day: int
    files: list[SlideFile] = Field(default_factory=list)


class Course(BaseModel):
    code: str
    name: str
    description: str = ""
    classmates: str = ""
    days: list[CourseDay] = Field(default_factory=list)


class CourseSummary(BaseModel):
    code: str
    name: str
    description: str
    read_percent: int
    total_days: int
