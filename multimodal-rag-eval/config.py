"""Configuration for Multimodal RAG with Evaluation."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # API Keys
    openai_api_key: str = ""

    # Paths
    chroma_persist_dir: str = "./chroma_db"
    data_dir: str = "./data"
    uploads_dir: str = "./data/uploads"

    # Models
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    ragas_evaluator_model: str = "gpt-4o-mini"

    # RAG Settings
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k_retrieval: int = 5
    hybrid_vector_weight: float = 0.7  # 70% vector, 30% BM25

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


def ensure_dirs(settings: Settings) -> None:
    """Ensure required directories exist."""
    Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.uploads_dir).mkdir(parents=True, exist_ok=True)
