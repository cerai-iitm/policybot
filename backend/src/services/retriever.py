import asyncio
import os
import warnings
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np
from huggingface_hub import InferenceClient
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import FieldCondition, Filter, MatchAny
from qdrant_client.models import QueryRequest
from sqlalchemy.ext.asyncio import AsyncSession
from transformers import logging as hf_logging

from src.core import cfg, logger
from src.core.util import free_embedding_model, load_embedding_model
from src.db.crud import get_summary_by_source_name
from src.services.LLM_interface import LLM_Interface
from src.services.vllm_embeddings import get_vllm_query_embeddings

# set HF logging verbosity once at module import
hf_logging.set_verbosity_error()

warnings.filterwarnings(
    "ignore", message="You're using a XLMRobertaTokenizerFast tokenizer.*"
)
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")


class Retriever:
    def __init__(
        self,
        interface: LLM_Interface,
        top_k: int = 5,
    ) -> None:
        self.top_k = top_k
        self.interface = interface

    def _softmax_top_p_filter(self, scores, items, top_p, temperature):
        scores = np.array(scores)
        exp_scores = np.exp((scores - np.max(scores)) / temperature)
        softmax_scores = exp_scores / exp_scores.sum()
        sorted_indices = np.argsort(-softmax_scores)
        sorted_items = [items[i] for i in sorted_indices]
        sorted_softmax_scores = softmax_scores[sorted_indices]
        cumsum = np.cumsum(sorted_softmax_scores)
        cutoff_index = np.searchsorted(cumsum, top_p) + 1
        selected_items = sorted_items[:cutoff_index]
        logger.debug(f"Softmax scores: {sorted_softmax_scores}")
        return selected_items

    def reciprocal_rank_fusion(self, query_ids: List, k: int):
        scores = defaultdict(float)
        debug_count = 0
        for query in query_ids:
            for rank, chunk_id in enumerate(query, start=1):
                scores[chunk_id] += 1.0 / (k + rank)
                debug_count += 1
        logger.debug(f"Total chunk count for reciprocal rank fusion: {debug_count}")

        chunk_ids = np.array(list(scores.keys()))
        score_values = np.array(list(scores.values()))

        top_p = cfg.TOP_P

        selected_chunk_ids = self._softmax_top_p_filter(
            scores=score_values,
            items=chunk_ids.tolist(),
            top_p=top_p,
            temperature=cfg.RRF_TEMP,
        )
        return selected_chunk_ids

    def rerank_chunks(self, query: str, chunks: List[str]) -> List[str]:
        try:
            logger.info(f"Applying reranking to filtered chunks: {len(chunks)} chunks")
            if not chunks:
                logger.warning("No chunks provided for reranking.")
                return []

            # Call TEI rerank endpoint using requests
            import requests

            response = requests.post(
                f"{cfg.TEI_RERANKER_URL}/rerank",
                json={"query": query, "texts": chunks},
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            results = response.json()

            # Parse response: [{"index": 0, "score": 0.95}, ...]
            if not results or not isinstance(results, list):
                logger.error(f"Invalid TEI response: {results}")
                return chunks

            # Extract scores in order of chunks using index
            scores = [0.0] * len(chunks)
            for item in results:
                if "index" in item and "score" in item:
                    idx = item["index"]
                    if 0 <= idx < len(chunks):
                        scores[idx] = item["score"]

            scores = np.array(scores)

            selected_chunks = self._softmax_top_p_filter(
                scores=scores,
                items=chunks,
                top_p=cfg.TOP_P,
                temperature=cfg.RERANKER_TEMP,
            )
            logger.debug(f"Number of chunks after reranking: {len(selected_chunks)}")
            return selected_chunks
        except Exception as e:
            logger.error(f"Error during reranking: {e}")
            return chunks

    async def _generate_query_embeddings(
        self, rewritten_queries: List[str]
    ) -> np.ndarray:
        """Generate embeddings for rewritten queries.

        Uses vLLM async call if enabled (single batch),
        otherwise falls back to local HuggingFace model in thread.
        """
        if cfg.VLLM_EMBEDDING_ENABLED:
            # Use vLLM - async single batch request
            return await get_vllm_query_embeddings(rewritten_queries)
        else:
            # Fallback to local HuggingFace model in thread
            def embed_sync():
                embedding_model, device = load_embedding_model(None)
                try:
                    embeddings = []
                    for rq in rewritten_queries:
                        embeddings.append(embedding_model.embed_query(rq))
                    return np.array(embeddings, dtype=np.float32)
                finally:
                    free_embedding_model(embedding_model, device)

            return await asyncio.to_thread(embed_sync)

    async def retrieve(
        self,
        query: str,
        pdfs: List[str],
        db: Optional[AsyncSession] = None,
        top_k: Optional[int] = None,
    ) -> Tuple[List[str], List[Dict[str, any]]]:
        if top_k is None:
            top_k = self.top_k

        try:
            # Initialize variables for local model (only used if vLLM is disabled)
            embedding_model = None
            device = None

            # Only load local embedding model if NOT using vLLM
            if not cfg.VLLM_EMBEDDING_ENABLED:
                logger.info("Loading embedding model (threaded)...")
                embedding_model, device = await asyncio.to_thread(
                    load_embedding_model, None
                )
            else:
                logger.info("Using vLLM for embeddings (no local model loading)")

            logger.info("Generating rewritten queries for better retrieval")
            # Fetch source summaries asynchronously if a DB session is provided.
            if db is not None and pdfs:
                coros = [
                    get_summary_by_source_name(db, os.path.basename(pdf))
                    for pdf in pdfs
                ]
                summaries = await asyncio.gather(*coros)
            else:
                if pdfs:
                    logger.warning("No DB session provided; skipping source summaries.")
                summaries = []

            summary = "\n\n".join(filter(None, summaries)) if summaries else ""
            # Use batched query generation (2-in-1 for vLLM, sequential fallback for others)
            rewritten_queries = await self.interface.generate_rewritten_queries_batched(
                query=query, summary=summary
            )

            logger.info("Generating query embeddings")
            # Generate embeddings - async vLLM or threaded local model
            query_embeddings = await self._generate_query_embeddings(rewritten_queries)

            # Free embedding model resources only if we loaded local model
            if not cfg.VLLM_EMBEDDING_ENABLED and embedding_model is not None:
                await asyncio.to_thread(free_embedding_model, embedding_model, device)

            logger.info("Connecting to Qdrant")
            client = AsyncQdrantClient(host=cfg.QDRANT_HOST, port=cfg.QDRANT_PORT)

            # Qdrant filter for all sources in pdfs
            filter_ = Filter(
                must=[FieldCondition(key="source", match=MatchAny(any=pdfs))]
            )
            logger.info(f"Using filter for sources: {pdfs}")

            logger.info("Retrieving relevant chunks from Qdrant")

            requests = [
                QueryRequest(
                    query=embedding.tolist(),
                    limit=top_k,
                    filter=filter_,
                    with_payload=True,
                )
                for embedding in query_embeddings
            ]

            results = await client.query_batch_points(
                collection_name=cfg.COLLECTION_NAME,
                requests=requests,
            )
            await client.close()

            chunk_texts = []
            chunk_ids = []
            chunk_metadata = []
            for query_response in results:
                for point in query_response.points:
                    point_id = point.id
                    text = (
                        point.payload.get("text", "No text found")
                        if point.payload
                        else "No text found"
                    )
                    metadata = {
                        "source": point.payload.get("source", "Unknown")
                        if point.payload
                        else "Unknown",
                        "page_number": point.payload.get("page_number", None)
                        if point.payload
                        else None,
                    }
                    chunk_ids.append(point_id)
                    chunk_texts.append(text)
                    chunk_metadata.append(metadata)

            id_to_doc = dict(zip(chunk_ids, chunk_texts))
            id_to_metadata = dict(zip(chunk_ids, chunk_metadata))
            logger.info(f"Retrieved len(chunk_texts): {len(chunk_texts)} chunks")

            ids_per_query = [
                [point.id for point in result.points] for result in results
            ]

            ranked_chunk_ids = await asyncio.to_thread(
                self.reciprocal_rank_fusion, ids_per_query, k=top_k
            )
            filtered_chunks = [
                id_to_doc[chunk_id]
                for chunk_id in ranked_chunk_ids
                if chunk_id in id_to_doc
            ]

            logger.info(f"Number of chunks after rank fusion: {len(filtered_chunks)}")
            logger.info("Performing reranking on filtered chunks")
            reranked_chunks = await asyncio.to_thread(
                self.rerank_chunks, query, filtered_chunks
            )

            # Build corresponding metadata list for reranked chunks
            reranked_metadata = [
                id_to_metadata[chunk_id]
                for chunk_id in ranked_chunk_ids
                if chunk_id in id_to_metadata
            ][: len(reranked_chunks)]  # Match length after reranking filtering

            return reranked_chunks, reranked_metadata

        except Exception as e:
            logger.error(f"Error retrieving data: {e}")
            return [], []


if __name__ == "__main__":
    import asyncio
    import os

    from qdrant_client import AsyncQdrantClient
    from qdrant_client.http.models import FieldCondition, Filter, MatchAny
    from qdrant_client.models import QueryRequest

    from src.core import cfg, free_embedding_model, load_embedding_model, logger

    # 1. Define query and sources
    query = "What are some specific examples of AI applications prohibited by the EU AI Act?"
    pdfs = [
        "Future-of-Life-InstituteAI-Act-overview-30-May-2024.pdf"
    ]  # Replace with your actual source names
    logger.info(f"Query: {query}")
    logger.info(f"PDFs/Sources: {pdfs}")

    # 2. Load embedding model
    embedding_model, device = load_embedding_model("cpu")
    logger.info(f"Loaded embedding model on device: {device}")

    # 3. Encode query
    try:
        query_embedding = embedding_model.embed_query(query)
        logger.info(f"Query embedding: {query_embedding}")
        logger.info(f"Embedding shape: {len(query_embedding)}")
    except Exception as e:
        logger.error(f"Error encoding query: {e}")

    # 4. Connect to Qdrant
    try:
        client = AsyncQdrantClient(host=cfg.QDRANT_HOST, port=cfg.QDRANT_PORT)
        logger.info(f"Connected to Qdrant at {cfg.QDRANT_HOST}:{cfg.QDRANT_PORT}")
    except Exception as e:
        logger.error(f"Error connecting to Qdrant: {e}")

    # 5. Build Qdrant filter
    try:
        filter_ = Filter(must=[FieldCondition(key="source", match=MatchAny(any=pdfs))])
        logger.info(f"Qdrant filter: {filter_}")
    except Exception as e:
        logger.error(f"Error building Qdrant filter: {e}")

    # 6. Query Qdrant directly
    async def direct_query():
        try:
            query_requests = [
                QueryRequest(
                    query=query_embedding,
                    limit=5,
                    filter=filter_,
                    with_payload=True,
                )
            ]
            logger.info(f"QueryRequest: {query_requests}")

            results = await client.query_batch_points(
                collection_name=cfg.COLLECTION_NAME,
                requests=query_requests,
            )
            logger.info(f"Raw Qdrant results: {results}")
            logger.info(f"Type of results: {type(results)}")
        except Exception as e:
            logger.error(f"Error querying Qdrant: {e}")
            return

        # 7. Iterate over results
        chunk_texts = []
        chunk_ids = []
        for i, query_response in enumerate(results):
            logger.info(f"QueryResponse {i}: {query_response}")
            logger.info(f"Type of QueryResponse: {type(query_response)}")
            for j, point in enumerate(query_response.points):
                logger.info(f"Point {j}: {point}")
                logger.info(f"Point ID: {getattr(point, 'id', None)}")
                logger.info(f"Point payload: {getattr(point, 'payload', None)}")
                text = (
                    point.payload.get("text", "No text found")
                    if point.payload
                    else "No text found"
                )
                chunk_texts.append(text)
                chunk_ids.append(point.id)

        logger.info(f"All chunk_texts: {chunk_texts}")
        logger.info(f"All chunk_ids: {chunk_ids}")

        id_to_doc = dict(zip(chunk_ids, chunk_texts))
        logger.info(f"id_to_doc mapping: {id_to_doc}")

        await client.close()
        logger.info("Closed Qdrant client.")

    asyncio.run(direct_query())

    # 8. Free embedding model
    free_embedding_model(embedding_model, device)
    logger.info("Freed embedding model.")
    logger.info("Freed embedding model.")
