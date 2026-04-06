import numpy as np
from typing import List
from FlagEmbedding import FlagReranker

from src.core import cfg

from .base import BaseReranker


class FlagRerankerWrapper(BaseReranker):
    def __init__(self, model_name: str | None = None):
        self.reranker = FlagReranker(
            model_name or cfg.RERANKING_MODEL_NAME,
            use_fp16=True,
        )

    def rerank(self, query: str, chunks: List[str]) -> List[str]:
        if not chunks:
            return []

        pairs = [[query, chunk] for chunk in chunks]
        scores = self.reranker.compute_score(pairs)

        if isinstance(scores, float):
            scores = [scores]

        sorted_chunks = self._sort_by_scores(chunks, scores)
        return sorted_chunks, scores

    def _sort_by_scores(self, chunks: List[str], scores: List[float]) -> List[str]:
        scores = np.array(scores)
        sorted_indices = np.argsort(-scores)
        return [chunks[i] for i in sorted_indices]
