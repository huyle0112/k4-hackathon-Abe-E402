from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.courses import router as courses_router
from app.api.health import router as health_router
from app.config import get_settings
from app.rag.vector_store import JsonVectorStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.store = JsonVectorStore(get_settings().vector_store_path)
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
