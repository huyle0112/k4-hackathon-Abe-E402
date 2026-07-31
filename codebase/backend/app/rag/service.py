from __future__ import annotations

from app.rag.generation.generator import AnswerGenerator
from app.rag.models import ChatResponse, RetrievalRequest
from app.rag.retrieval.retriever import Retriever


class RAGService:
    def __init__(
        self,
        *,
        retriever: Retriever,
        generator: AnswerGenerator,
    ) -> None:
        self.retriever = retriever
        self.generator = generator

    def ask(
        self,
        query: str,
        *,
        session_numbers: list[int] | None = None,
        top_k: int = 5,
    ) -> ChatResponse:
        request = RetrievalRequest(
            query=query,
            session_numbers=session_numbers,
            top_k=top_k,
        )
        hits = self.retriever.retrieve(request)
        required_sessions = (
            request.session_numbers
            if request.session_numbers
            and len(request.session_numbers) >= 2
            else None
        )
        generated = self.generator.generate(
            request.query,
            hits,
            required_session_numbers=required_sessions,
        )
        return ChatResponse(
            **generated.model_dump(),
            retrieval_hits=hits,
        )
