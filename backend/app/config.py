from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}

    # Database
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/policybot"
    )

    # JWT Settings
    jwt_secret: str = "change-me-in-production"
    jwt_access_expire_minutes: int = 30

    # LLM Settings
    llm_provider: str = "vllm"
    default_model: str = "gemma3n:e4b"
    vllm_llm_url: str = "http://localhost:8080/v1"
    gemini_api_key: str | None = None
    ollama_url: str = "http://localhost:11434"

    # Direct API Keys (optional)
    vllm_llm_api_key: str | None = None
    ollama_api_key: str | None = None

    # Embedding Settings
    embedding_provider: str = "vllm"
    vllm_embedding_url: str = "http://localhost:8080/v1"
    vllm_embedding_model: str = "bge-base-en-v1.5"
    vllm_embedding_api_key: str | None = None
    sentence_transformers_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Reranker Settings
    reranker_provider: str = "tei"
    tei_reranker_url: str = "http://localhost:8081"
    flag_reranker_model: str | None = None
    top_k: int = 10
    top_p: float = 0.9
    reranker_temp: float = 1.0
    rrf_temp: float = 0.17

    # Dev Proxy Settings (used when DEV_PROXY_API_KEY is set)
    dev_proxy_api_key: str | None = None
    vllm_llm_proxy_url: str | None = None
    ollama_proxy_url: str | None = None
    vllm_embedding_proxy_url: str | None = None

    # File storage
    upload_dir: str = "uploads"

    # PDF Processing
    max_concurrent_processing: int = 2

    # Qdrant Vector Database
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    q_collection_name: str = "pdf_embeddings"

    # PDF Processing
    breakpoint_threshold_type: str = "standard_deviation"
    breakpoint_threshold_amount: float = 1.0

    # RAG Settings
    num_rewritten_queries: int = 5
    max_history_messages: int = 3

    # Deployment environment name. Recommended env var: ENVIRONMENT
    # Allowed values: "development" or "production"
    # Validation is enforced via Pydantic Literal type.
    environment: Literal["development", "production"] = "production"


@lru_cache()
def get_config() -> Config:
    return Config()
