from src.core import cfg

from .reranker import FlagRerankerWrapper, TEIReranker, BaseReranker


def get_reranker(provider: str | None = None) -> BaseReranker:
    provider = (provider or cfg.RERANKER_PROVIDER).lower()

    if provider == "tei":
        return TEIReranker()

    if provider == "flag":
        return FlagRerankerWrapper()

    # Default fallback
    return TEIReranker()
