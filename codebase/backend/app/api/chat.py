from fastapi import APIRouter, Request

from app.config import get_settings
from app.rag.generation.generator import generate_answer
from app.rag.models import ChatRequest, ChatResponse
from app.rag.retrieval.retriever import retrieve

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    settings = get_settings()
    session_ids = [payload.course_code] if payload.course_code else None
    file_names = [payload.slide_id] if payload.slide_id else None

    hits = retrieve(
        payload.question,
        request.app.state.store,
        payload.top_k or settings.top_k,
        session_ids,
        file_names,
    )
    return generate_answer(payload.question, hits, settings.confidence_threshold)
