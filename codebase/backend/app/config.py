from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VLearn Cross-session Tutor"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    vector_store_path: Path = Path("vector-store/chunks.json")
    top_k: int = 5
    confidence_threshold: float = 0.12

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
