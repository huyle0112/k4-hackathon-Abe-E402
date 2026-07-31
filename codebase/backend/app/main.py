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
    from app.rag.runtime import create_rag_service
    rag_service = create_rag_service(settings)
    vector_store = rag_service.retriever.vector_store
    embedding_provider = rag_service.retriever.embedding_provider
    retriever = rag_service.retriever
    generator = rag_service.generator
    

    
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
