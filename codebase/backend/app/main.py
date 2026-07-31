from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.agent import AgentTools
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.mindmaps import router as mindmaps_router
from app.api.courses import router as courses_router
from app.config import get_settings
from app.mindmaps import (
    MindmapRepository,
    MindmapService,
    OpenAIMindmapProvider,
    PDFMindmapContextProvider,
)
from app.rag.ingestion.chunker import SlideChunker
from app.rag.ingestion.pdf_loader import PDFLoader
from app.rag.runtime import (
    create_rag_service,
)

load_dotenv()


def _cors_origins() -> list[str]:
    raw = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.rag_service = create_rag_service(settings)
    mindmap_provider = (
        OpenAIMindmapProvider(settings)
        if settings.llm_provider and settings.llm_model
        else None
    )
    app.state.mindmap_service = MindmapService(
        repository=MindmapRepository(settings.database_path),
        context_provider=PDFMindmapContextProvider(
            settings.lessons_dir,
            loader=PDFLoader(ocr_enabled=settings.ocr_enabled),
            chunker=SlideChunker(
                max_tokens=settings.chunk_max_tokens,
                overlap_tokens=settings.chunk_overlap_tokens,
            ),
        ),
        generation_provider=mindmap_provider,
    )
    app.state.agent_tools = AgentTools(
        embedding_provider=app.state.rag_service.retriever.embedding_provider,
        vector_store=app.state.rag_service.retriever.vector_store,
        reranker=app.state.rag_service.retriever.reranker,
        mindmap_service=app.state.mindmap_service,
        candidate_k=settings.retrieval_candidate_k,
    )
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title=os.getenv("APP_NAME", "VLearn Cross-session Tutor"),
        version="1.0.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health_router, prefix="/api")
    application.include_router(chat_router, prefix="/api")
    application.include_router(mindmaps_router, prefix="/api")
    application.include_router(courses_router)

    @application.get("/")
    def root() -> dict[str, str]:
        return {"name": application.title, "docs": "/docs"}

    return application


app = create_app()
