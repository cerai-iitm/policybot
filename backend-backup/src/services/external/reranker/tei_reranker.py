import numpy as np
from typing import List, Tuple
import requests

from src.core import cfg

from .base import BaseReranker


class TEIReranker(BaseReranker):
    def rerank(self, query: str, chunks: List[str]) -> Tuple[List[str], List[float]]:
        """Send query and list of chunks to the TEI reranker endpoint.

        Returns a tuple of (sorted_chunks, scores) where ``sorted_chunks`` are ordered
        from highest to lowest score.
        """
        if not chunks:
            return [], []

        headers = {"Content-Type": "application/json"}
        if cfg.DEV_PROXY_API_KEY:
            headers["X-API-Key"] = cfg.DEV_PROXY_API_KEY

        response = requests.post(
            f"{cfg.TEI_RERANKER_URL}/rerank",
            json={"query": query, "texts": chunks},
            headers=headers,
        )
        response.raise_for_status()
        results = response.json()

        # If the service returns something unexpected, fallback to the original order.
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
        scores = np.array(scores)
        sorted_indices = np.argsort(-scores)
        return [chunks[i] for i in sorted_indices]
