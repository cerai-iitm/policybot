from langchain_core.embeddings.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr

from src.core import cfg


def get_embedding_model(
    provider: str | None = None,
    model_name: str | None = None,
) -> Embeddings:
    provider = (provider or cfg.EMBEDDING_PROVIDER).lower()

    if provider == "vllm":
        headers = (
            {"X-API-Key": cfg.DEV_PROXY_API_KEY} if cfg.DEV_PROXY_API_KEY else None
        )
        return OpenAIEmbeddings(
            model=model_name or cfg.VLLM_EMBEDDING_MODEL,
            base_url=cfg.VLLM_EMBEDDING_URL,
            api_key=SecretStr(cfg.VLLM_EMBEDDING_API_KEY) or SecretStr("no-key"),
            default_headers=headers,
        )

    if provider == "sentence-transformers":
        return HuggingFaceEmbeddings(
            model_name=model_name or cfg.EMBEDDING_MODEL_NAME,
            model_kwargs=cfg.EMBEDDING_MODEL_KWARGS,
            encode_kwargs=cfg.ENCODE_KWARGS,
        )

    # Default fallback to sentence-transformers
    return HuggingFaceEmbeddings(
        model_name=model_name or cfg.EMBEDDING_MODEL_NAME,
        model_kwargs=cfg.EMBEDDING_MODEL_KWARGS,
        encode_kwargs=cfg.ENCODE_KWARGS,
    )


def get_embedding_provider(model_name: str | None = None) -> Embeddings:
    return get_embedding_model(model_name=model_name)
