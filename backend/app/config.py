from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # Database
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/policybot"
    )

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
