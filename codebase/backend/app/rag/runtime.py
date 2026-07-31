from __future__ import annotations

from app.config import Settings
from app.rag.embeddings import (
    EmbeddingProvider,
    create_embedding_provider,
)
from app.rag.generation.generator import AnswerGenerator
from app.rag.retrieval.reranker import BaselineReranker
from app.rag.retrieval.retriever import Retriever
from app.rag.service import RAGService
from app.rag.vector_store import ChromaVectorStore


def create_vector_store(
    settings: Settings,
    embedding_provider: EmbeddingProvider,
) -> ChromaVectorStore:
    return ChromaVectorStore(
        path=settings.vector_store_dir,
        collection_name=settings.collection_name,
        embedding_provider_name=embedding_provider.name,
        embedding_model_name=embedding_provider.model,
        embedding_dimension=embedding_provider.dimension,
    )


def create_rag_service(settings: Settings) -> RAGService:
    embedding_provider = create_embedding_provider(settings)
    vector_store = create_vector_store(settings, embedding_provider)
    retriever = Retriever(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        reranker=BaselineReranker(),
        candidate_k=settings.retrieval_candidate_k,
        score_threshold=settings.retrieval_score_threshold,
    )
    generator = AnswerGenerator(
        abstention_threshold=settings.retrieval_score_threshold,
        minimum_lexical_coverage=settings.retrieval_min_lexical_coverage,
        minimum_vector_score=settings.retrieval_min_vector_score,
    )
    return RAGService(retriever=retriever, generator=generator)
