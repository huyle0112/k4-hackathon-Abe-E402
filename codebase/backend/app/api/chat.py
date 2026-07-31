from fastapi import APIRouter, Request

from app.config import get_settings
from app.rag.models import FEChatRequest, FEChatResponse, FECitation, RetrievalRequest
from app.rag.retrieval.retriever import Retriever

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat", response_model=FEChatResponse)
def chat(payload: FEChatRequest, request: Request) -> FEChatResponse:
    settings = get_settings()
    retriever: Retriever = request.app.state.retriever
    generator = request.app.state.generator

    session_numbers = []
    if payload.slide_id and payload.slide_id.startswith("D"):
        try:
            day = int(payload.slide_id[1:3])
            session_numbers.append(day)
        except ValueError:
            pass

    retrieval_request = RetrievalRequest(
        query=payload.question,
        session_numbers=session_numbers if session_numbers else None,
        top_k=payload.top_k or settings.retrieval_top_k
    )

    hits = retriever.retrieve(retrieval_request)

    # Calculate initial confidence based on retriever logic from generator
    scores = [max(0.0, min(1.0, hit.score)) for hit in hits[:3]]
    if not scores:
        base_confidence = 0.0
    else:
        top_score = scores[0]
        mean_score = sum(scores) / len(scores)
        unique_documents = len({hit.chunk.document_id for hit in hits[:3]})
        source_support = min(1.0, unique_documents / 2)
        margin = max(0.0, top_score - scores[1]) if len(scores) > 1 else top_score
        base_confidence = round(max(0.0, min(1.0, (
            top_score * 0.55 + mean_score * 0.25 + source_support * 0.10 + min(1.0, margin * 2) * 0.10
        ))), 4)

    generation_result = generator._generate_structured(
        query=payload.question,
        context_hits=hits,
        confidence=base_confidence,
        required_sessions=session_numbers
    )

    status = "error"
    if generation_result.abstained:
        if "scope" in (generation_result.reason or "").lower():
            status = "out_of_scope"
        else:
            status = "low_confidence"
    elif generation_result.confidence < settings.retrieval_score_threshold:
        status = "low_confidence"
    else:
        status = "ok"
    
    fe_sources = []
    for citation in generation_result.citations:
        fe_sources.append(FECitation(
            slide_id=citation.chunk_id,
            day=citation.slide_number,
            page=citation.slide_number,
            file_name=citation.source_file,
            relevance_score=generation_result.confidence
        ))

    return FEChatResponse(
        answer=generation_result.answer,
        confidence=generation_result.confidence,
        status=status,
        sources=fe_sources
    )
