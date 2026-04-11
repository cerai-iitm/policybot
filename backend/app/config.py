from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Config(BaseSettings):
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

    # Dev Proxy Settings (used when DEV_PROXY_API_KEY is set)
    dev_proxy_api_key: str | None = None
    vllm_llm_proxy_url: str | None = None
    ollama_proxy_url: str | None = None

    # Deployment environment name. Recommended env var: ENVIRONMENT
    # Allowed values: "development" or "production"
    # Validation is enforced via Pydantic Literal type.
    environment: Literal["development", "production"] = "production"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_config() -> Config:
    return Config()
