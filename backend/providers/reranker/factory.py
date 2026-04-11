# providers/reranker/factory.py
from abc import ABC, abstractmethod
from typing import List, Tuple

from app.config import get_config

config = get_config()


class BaseReranker(ABC):
    @abstractmethod
    def rerank(self, query: str, chunks: List[str]) -> Tuple[List[str], List[float]]:
        pass


class TEIReranker(BaseReranker):
    def rerank(self, query: str, chunks: List[str]) -> Tuple[List[str], List[float]]:
        import numpy as np
        import requests

        if not chunks:
            return [], []

        headers = {"Content-Type": "application/json"}
        if config.dev_proxy_api_key:
            headers["X-API-Key"] = config.dev_proxy_api_key

        url = config.tei_reranker_url
        response = requests.post(
            f"{url}/rerank",
            json={"query": query, "texts": chunks},
            headers=headers,
        )
        response.raise_for_status()
        results = response.json()

        if not results or not isinstance(results, list):
            return chunks, []

        scores = [0.0] * len(chunks)
        for item in results:
            if "index" in item and "score" in item:
                idx = item["index"]
                if 0 <= idx < len(chunks):
                    scores[idx] = item["score"]

        sorted_chunks = self._sort_by_scores(chunks, scores)
        return sorted_chunks, scores

    def _sort_by_scores(self, chunks: List[str], scores: List[float]) -> List[str]:
        scores_arr = np.array(scores)
        sorted_indices = np.argsort(-scores_arr)
        return [chunks[i] for i in sorted_indices]


class FlagRerankerWrapper(BaseReranker):
    def rerank(self, query: str, chunks: List[str]) -> Tuple[List[str], List[float]]:
        from sentence_transformers import CrossEncoder

        if not chunks:
            return [], []

        model_name = config.flag_reranker_model or "BAAI/bge-reranker-base"
        model = CrossEncoder(model_name)

        pairs = [[query, chunk] for chunk in chunks]
        scores = model.predict(pairs)

        sorted_chunks = self._sort_by_scores(chunks, scores)
        return sorted_chunks, scores.tolist()

    def _sort_by_scores(self, chunks: List[str], scores) -> List[str]:
        sorted_indices = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )
        return [chunks[i] for i in sorted_indices]


def get_reranker() -> BaseReranker:
    """Factory function to get reranker based on config."""
    provider = config.reranker_provider.lower()

    if provider == "tei":
        return TEIReranker()

    if provider == "flag":
        return FlagRerankerWrapper()

    raise ValueError(f"Unknown reranker provider: {provider}")
