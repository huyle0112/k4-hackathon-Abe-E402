from __future__ import annotations

from app.config import Settings
from app.agent.router import LLMTaskRouter
from app.rag.embeddings import (
    EmbeddingProvider,
    create_embedding_provider,
)
from app.rag.generation.generator import (
    AnswerGenerator,
    create_text_generation_provider,
)
from app.rag.retrieval.reranker import BaselineReranker
from app.rag.retrieval.retriever import Retriever
from app.rag.service import RAGService
from app.rag.vector_store import ChromaVectorStore


def create_vector_store(
    settings: Settings,
    embedding_provider: EmbeddingProvider,
    *,
    allow_incompatible: bool = False,
) -> ChromaVectorStore:
    return ChromaVectorStore(
        path=settings.vector_store_dir,
        collection_name=settings.collection_name,
        embedding_provider_name=embedding_provider.name,
        embedding_model_name=embedding_provider.model_name,
        embedding_dimension=embedding_provider.dimension,
        allow_incompatible=allow_incompatible,
    )


def create_rag_service(
    settings: Settings,
    *,
    llm_client: object | None = None,
) -> RAGService:
    embedding_provider = create_embedding_provider(settings)
    vector_store = create_vector_store(settings, embedding_provider)
    retriever = Retriever(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        reranker=BaselineReranker(),
        candidate_k=settings.retrieval_candidate_k,
        score_threshold=settings.retrieval_score_threshold,
        minimum_session_evidence=(
            settings.retrieval_min_session_evidence
        ),
    )
    text_generation_provider = create_text_generation_provider(
        settings,
        client=llm_client,
    )
    task_router = (
        LLMTaskRouter(
            api_key=settings.llm_api_key or "",
            model=settings.llm_model or "",
            base_url=settings.llm_base_url,
            timeout=settings.llm_timeout_seconds,
            max_retries=settings.llm_max_retries,
            client=llm_client,
        )
        if settings.llm_provider == "openai"
        and settings.llm_api_key
        and settings.llm_model
        and llm_client is None
        else None
    )
    generator = AnswerGenerator(
        provider=text_generation_provider,
        abstention_threshold=settings.retrieval_score_threshold,
        minimum_lexical_coverage=settings.retrieval_min_lexical_coverage,
        minimum_vector_score=settings.retrieval_min_vector_score,
        maximum_context_chunks=settings.generation_max_context_chunks,
        maximum_context_tokens=settings.generation_max_context_tokens,
        minimum_session_evidence=(
            settings.retrieval_min_session_evidence
        ),
    )
    return RAGService(
        retriever=retriever,
        generator=generator,
        task_router=task_router,
    )
