# providers/embedding/factory.py
from langchain_core.embeddings.embeddings import Embeddings

from app.config import get_config

config = get_config()


def get_embedding() -> Embeddings:
    """Factory function to get embedding model based on config."""
    provider = config.embedding_provider.lower()

    use_proxy = config.dev_proxy_api_key is not None and config.dev_proxy_api_key != ""
    proxy_headers = {"X-API-Key": config.dev_proxy_api_key} if use_proxy else None

    if provider == "vllm":
        import httpx
        from langchain_openai import OpenAIEmbeddings
        from pydantic import SecretStr

        url = (
            config.vllm_embedding_proxy_url if use_proxy else config.vllm_embedding_url
        )
        api_key = config.vllm_embedding_api_key or "EMPTY"

        # Ensure URL ends with /v1 for OpenAI-compatible API
        if not url.endswith("/v1"):
            url = url.rstrip("/") + "/v1"

        # Create both sync and async clients with proxy headers
        http_client = httpx.Client(headers=proxy_headers) if use_proxy else None
        http_async_client = (
            httpx.AsyncClient(headers=proxy_headers) if use_proxy else None
        )

        return OpenAIEmbeddings(
            model=config.vllm_embedding_model,
            base_url=url,
            api_key=SecretStr(api_key),
            http_client=http_client,
            http_async_client=http_async_client,
            timeout=60.0,
        )

    if provider == "sentence-transformers":
        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(
            model_name=config.sentence_transformers_model,
        )

    raise ValueError(f"Unknown embedding provider: {provider}")
