import pytest
from src.services.external import get_embedding_provider
from langchain_core.embeddings.embeddings import Embeddings


def test_factory_returns_embeddings():
    """The factory should return an object implementing the Embeddings interface."""
    model = get_embedding_provider()
    assert isinstance(model, Embeddings)
    # We avoid heavy embedding calls in CI. Just verify the provider supplies the expected method.
    assert hasattr(model, "embed_query")
