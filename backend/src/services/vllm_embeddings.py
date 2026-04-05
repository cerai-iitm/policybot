"""Stateless vLLM embedding service for both documents and queries.

This module provides async, stateless interfaces to vLLM's OpenAI-compatible
embeddings endpoint. Each request creates a fresh AsyncOpenAI client that
auto-cleans when it goes out of scope.
"""

import asyncio
from typing import List, Optional

import numpy as np
from langchain_core.documents import Document
from openai import AsyncOpenAI

from src.core import cfg, logger


def format_query_for_gemma(query: str) -> str:
    """Format query for Gemma 300M embedding model.

    Uses the recommended format: task: search result | query: {query}

    Args:
        query: The raw user query string

    Returns:
        Formatted query string for Gemma 300M
    """
    return f"task: search result | query: {query}"


def format_document_for_gemma(title: str, text: str) -> str:
    """Format document for Gemma 300M embedding model.

    Uses the recommended format: title: {title} | text: {text}

    Args:
        title: Document source/title
        text: Document content

    Returns:
        Formatted document string for Gemma 300M
    """
    return f"title: {title} | text: {text}"


async def get_vllm_query_embeddings(queries: List[str]) -> np.ndarray:
    """Generate query embeddings using vLLM - single batch request.

    Stateless design: fresh AsyncOpenAI client per request.
    Sends all queries as one batch (max ~20 items for retrieval).

    Args:
        queries: List of query strings to embed

    Returns:
        numpy array of shape (len(queries), 768) with float32 embeddings
    """
    if not queries:
        return np.array([], dtype=np.float32)

    # Stateless: fresh client per request, auto-cleanup on scope exit
    client_kwargs = {
        "api_key": cfg.VLLM_EMBEDDING_API_KEY,
        "base_url": cfg.VLLM_EMBEDDING_URL,
    }
    if cfg.DEV_PROXY_API_KEY:
        client_kwargs["default_headers"] = {"X-API-Key": cfg.DEV_PROXY_API_KEY}
    client = AsyncOpenAI(**client_kwargs)

    # Format queries for Gemma 300M if that's the model being used
    if "gemma" in cfg.VLLM_EMBEDDING_MODEL.lower():
        texts = [format_query_for_gemma(q) for q in queries]
    else:
        texts = queries

    # Single batch request - all queries at once
    response = await client.embeddings.create(
        input=texts, model=cfg.VLLM_EMBEDDING_MODEL
    )

    # Extract embeddings (768 dimensions for Gemma 300M)
    embeddings = [item.embedding for item in response.data]

    logger.info(f"Generated {len(embeddings)} query embeddings in one batch via vLLM")

    # Client goes out of scope here, automatically cleaned up
    return np.array(embeddings, dtype=np.float32)


async def get_vllm_document_embeddings(
    documents: List[Document], batch_size: int = 128, max_concurrent: int = 4
) -> Optional[np.ndarray]:
    """Generate document embeddings using vLLM with concurrent batching.

    Stateless design: fresh AsyncOpenAI client per batch.
    Maintains exactly `max_concurrent` requests to vLLM at all times,
    processing documents in batches until complete.

    Args:
        documents: List of Document objects to embed
        batch_size: Documents per batch (default 128)
        max_concurrent: Max parallel requests to vLLM (default 4)

    Returns:
        numpy array of shape (len(documents), 768) with float32 embeddings,
        or None if failed
    """
    if not documents:
        return None

    total_docs = len(documents)
    total_batches = (total_docs + batch_size - 1) // batch_size
    semaphore = asyncio.Semaphore(max_concurrent)
    all_embeddings = [None] * total_batches
    completed_batches = 0
    last_progress_time = asyncio.get_event_loop().time()

    async def embed_batch(batch_idx: int):
        """Worker: acquires semaphore, embeds batch, releases."""
        nonlocal completed_batches, last_progress_time
        async with semaphore:
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, total_docs)
            batch_docs = documents[start_idx:end_idx]

            # Stateless: fresh client per batch
            client_kwargs = {
                "api_key": cfg.VLLM_EMBEDDING_API_KEY,
                "base_url": cfg.VLLM_EMBEDDING_URL,
            }
            if cfg.DEV_PROXY_API_KEY:
                client_kwargs["default_headers"] = {"X-API-Key": cfg.DEV_PROXY_API_KEY}
            client = AsyncOpenAI(**client_kwargs)

            # Format documents for Gemma 300M if using that model
            if "gemma" in cfg.VLLM_EMBEDDING_MODEL.lower():
                texts = [
                    format_document_for_gemma(
                        doc.metadata.get("source", "unknown"), doc.page_content
                    )
                    for doc in batch_docs
                ]
            else:
                texts = [doc.page_content for doc in batch_docs]

            # Async API call
            response = await client.embeddings.create(
                input=texts, model=cfg.VLLM_EMBEDDING_MODEL
            )

            # Store in correct position to maintain order
            all_embeddings[batch_idx] = [item.embedding for item in response.data]
            completed_batches += 1

            # Check if 5 seconds passed since last progress update
            current_time = asyncio.get_event_loop().time()
            if current_time - last_progress_time >= 5.0:
                processed_docs = min(completed_batches * batch_size, total_docs)
                progress_pct = int((processed_docs / total_docs) * 100)
                logger.info(
                    f"Embedding progress: {completed_batches}/{total_batches} batches "
                    f"({processed_docs}/{total_docs} docs, {progress_pct}%)"
                )
                last_progress_time = current_time

            # Client goes out of scope, auto-cleanup

    # Process all batches with semaphore-controlled concurrency
    tasks = [embed_batch(i) for i in range(total_batches)]
    await asyncio.gather(*tasks)

    # Flatten embeddings maintaining document order
    embeddings = []
    for batch_embeddings in all_embeddings:
        embeddings.extend(batch_embeddings)

    logger.info(
        f"✓ Documents complete: {len(embeddings)}/{total_docs} embeddings "
        f"in {total_batches} batches ({max_concurrent} concurrent)"
    )

    return np.array(embeddings, dtype=np.float32)
