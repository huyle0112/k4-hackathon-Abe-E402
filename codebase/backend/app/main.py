from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.courses import router as courses_router
from app.api.health import router as health_router
from app.config import get_settings
from app.rag.embeddings import create_embedding_provider
from app.rag.generation.generator import create_text_generation_provider, AnswerGenerator
from app.rag.retrieval.retriever import Retriever
from app.rag.vector_store import ChromaVectorStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    
    # Initialize components
    vector_store = ChromaVectorStore(
        path=settings.vector_store_dir,
        collection_name=settings.collection_name,
        embedding_provider_name=settings.embedding_provider,
        embedding_dimension=settings.embedding_dimension,
        embedding_model_name=settings.embedding_model,
        allow_incompatible=True, # allow loading even if empty
    )
    
    embedding_provider = create_embedding_provider(settings)
    
    provider = create_text_generation_provider(settings)
    generator = AnswerGenerator(
        provider=provider,
        minimum_session_evidence=settings.retrieval_min_session_evidence,
    )
    
    retriever = Retriever(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        candidate_k=settings.retrieval_candidate_k,
        score_threshold=settings.retrieval_score_threshold,
        minimum_session_evidence=settings.retrieval_min_session_evidence,
    )
    
    app.state.store = vector_store
    app.state.retriever = retriever
    app.state.generator = generator
    
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health_router)
    application.include_router(courses_router)
    application.include_router(chat_router)

    @application.get("/")
    def root() -> dict[str, str]:
        return {"name": settings.app_name, "docs": "/docs"}

    return application


app = create_app()
