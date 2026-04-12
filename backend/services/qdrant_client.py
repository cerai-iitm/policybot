# services/qdrant_client.py
from qdrant_client import AsyncQdrantClient

from app.config import get_config


def get_qdrant_client() -> AsyncQdrantClient:
    config = get_config()
    return AsyncQdrantClient(host=config.qdrant_host, port=config.qdrant_port)
