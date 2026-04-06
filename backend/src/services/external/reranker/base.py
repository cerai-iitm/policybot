from abc import ABC, abstractmethod
from typing import List


class BaseReranker(ABC):
    @abstractmethod
    def rerank(self, query: str, chunks: List[str]) -> tuple[List[str], List[float]]:
        """Return a reordered list of chunks based on the query."""
        pass
