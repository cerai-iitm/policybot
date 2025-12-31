from __future__ import annotations

import logging
import os
import sys
import time
from typing import Callable, Optional

from huggingface_hub import snapshot_download

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("model-downloader")

EMBEDDING_MODEL_NAME = "Alibaba-NLP/gte-multilingual-base"
RERANKING_MODEL_NAME = "BAAI/bge-reranker-base"

# Defaults
DEFAULT_HF_HOME = "/app/cache/huggingface"
RETRIES = 3
BACKOFF_SECONDS = 2


def ensure_env() -> str:
    hf_home = os.environ.get("HF_HOME", DEFAULT_HF_HOME)
    os.environ["HF_HOME"] = hf_home
    logger.info("Using HF cache directory: %s", hf_home)
    return hf_home



def retry(fn: Callable[[], str], retries: int = RETRIES, backoff: int = BACKOFF_SECONDS) -> str:
    last_exc: Optional[Exception] = None
    delay = backoff
    for attempt in range(1, retries + 1):
        try:
            return fn()
        except Exception as e:
            last_exc = e
            logger.warning("Attempt %d/%d failed: %s", attempt, retries, e)
            if attempt < retries:
                logger.info("Retrying in %d seconds...", delay)
                time.sleep(delay)
                delay *= 2
    # Raise a clear error and chain the last exception for traceback
    if last_exc is not None:
        raise RuntimeError("All retry attempts failed") from last_exc
    raise RuntimeError("All retry attempts failed (no exception captured)")


def download(repo_id: str, cache_dir: str) -> str:
    logger.info("Downloading %s into %s (force download)...", repo_id, cache_dir)

    def _do():
        # force_download=True ensures we overwrite any existing cached snapshot for this repo
        return snapshot_download(repo_id=repo_id, cache_dir=cache_dir, force_download=False)

    path = retry(_do)
    logger.info("Downloaded %s -> %s", repo_id, path)
    return path


def main() -> int:
    try:
        cache_dir = ensure_env()
        download(EMBEDDING_MODEL_NAME, cache_dir)
        download(RERANKING_MODEL_NAME, cache_dir)
    except Exception as e:
        logger.exception("Model download failed: %s", e)
        return 1

    logger.info("All models downloaded successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
