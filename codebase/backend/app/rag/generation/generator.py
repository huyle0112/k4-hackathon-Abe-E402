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
