from fastapi import APIRouter, Request

from app.config import get_settings
from app.rag.generation.generator import generate_answer
from app.rag.models import ChatRequest, ChatResponse
from app.rag.retrieval.retriever import retrieve

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    settings = get_settings()
    hits = retrieve(
        payload.question,
        request.app.state.store,
        payload.top_k or settings.top_k,
        payload.session_ids,
        payload.file_names,
    )
    return generate_answer(payload.question, hits, settings.confidence_threshold)
