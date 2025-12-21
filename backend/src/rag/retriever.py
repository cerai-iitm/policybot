import asyncio
import os
import threading
import warnings
from collections import defaultdict
from typing import List, Optional

import numpy as np
from FlagEmbedding import FlagReranker
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import FieldCondition, Filter, MatchAny
from qdrant_client.models import QueryRequest
from sqlalchemy.ext.asyncio import AsyncSession
from transformers import logging as hf_logging

from src.config import cfg
from src.logger import logger
from src.rag.LLM_interface import LLM_Interface
from src.schema.source_summaries_crud import get_summary_by_source_name
from src.util import free_embedding_model, load_embedding_model

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
        # Lazily initialize FlagReranker to avoid blocking import/startup.
        # The actual heavy initialization will run in a background thread when needed.
        self.reranker: Optional[FlagReranker] = None
        self._reranker_init_lock = threading.Lock()
        self._reranker_ready = False

    def _init_reranker_sync(self):
        """Synchronous initializer for FlagReranker. Designed to be run inside
        a thread via asyncio.to_thread so it does not block the event loop.
        Multiple concurrent callers are guarded by a threading.Lock so init
        only happens once.
        """
        # Use a lock to ensure only one thread initializes the reranker
        with self._reranker_init_lock:
            if getattr(self, "_reranker_ready", False):
                return
            # Instantiate the heavy reranker synchronously
            self.reranker = FlagReranker(cfg.RERANKING_MODEL_NAME, use_fp16=True)
            self._reranker_ready = True
            logger.info("FlagReranker initialized (sync in background thread).")

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
            # Ensure reranker is available; try to initialize synchronously if it's not.
            # This method may be executed inside a thread (via asyncio.to_thread), so
            # calling the synchronous initializer here will not block the event loop.
            if self.reranker is None:
                try:
                    self._init_reranker_sync()
                except Exception as e:
                    logger.error(f"Reranker not available: {e}")
                    return chunks
            # Use a local variable to help type-checkers and avoid race windows.
            reranker = self.reranker
            if reranker is None:
                logger.error("Reranker unexpectedly None after init")
                return chunks
            scores = reranker.compute_score([(query, chunk) for chunk in chunks])
            scores = np.array(scores)
            if len(scores) != len(chunks):
                logger.error(
                    f"Mismatch between scores ({len(scores)}) and chunks ({len(chunks)})"
                )
                return chunks

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

    def _generate_query_embeddings_sync(self, embedding_model, rewritten_queries):
        """
        Synchronous helper to generate embeddings for a list of rewritten queries.
        This runs in a thread via asyncio.to_thread to avoid blocking the event loop.
        """
        embeddings = []
        for rq in rewritten_queries:
            embeddings.append(embedding_model.embed_query(rq))
        return np.array(embeddings, dtype=np.float32)

    async def retrieve(
        self,
        query: str,
        pdfs: List[str],
        db: Optional[AsyncSession] = None,
        top_k: Optional[int] = None,
    ) -> List[str]:
        if top_k is None:
            top_k = self.top_k

        try:
            logger.info("Loading embedding model (threaded)...")
            embedding_model, device = await asyncio.to_thread(
                load_embedding_model, None
            )

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
            rewritten_queries = await self.interface.generate_rewritten_queries(
                query=query, summary=summary
            )

            logger.info("Generating query embeddings (threaded)")
            # Generate embeddings in a thread (embedding_model.embed_query is sync/CPU-bound).
            query_embeddings = await asyncio.to_thread(
                self._generate_query_embeddings_sync, embedding_model, rewritten_queries
            )
            # Free embedding model resources in a thread as well.
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
            for query_response in results:
                for point in query_response.points:
                    point_id = point.id
                    text = (
                        point.payload.get("text", "No text found")
                        if point.payload
                        else "No text found"
                    )
                    chunk_ids.append(point_id)
                    chunk_texts.append(text)

            id_to_doc = dict(zip(chunk_ids, chunk_texts))
            logger.info(f"Retrieved len(chunk_texts): {len(chunk_texts)} chunks")

            ids_per_query = [
                [point.id for point in result.points] for result in results
            ]

            # Ensure FlagReranker is initialized before performing fusion/reranking.
            # Initialization runs synchronously but inside a background thread
            # so it does not block the event loop.
            await asyncio.to_thread(self._init_reranker_sync)

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
            return reranked_chunks

        except Exception as e:
            logger.error(f"Error retrieving data: {e}")
            return []


if __name__ == "__main__":
    import asyncio
    import os

    from qdrant_client import AsyncQdrantClient
    from qdrant_client.http.models import FieldCondition, Filter, MatchAny
    from qdrant_client.models import QueryRequest

    from src.config import cfg
    from src.logger import logger
    from src.util import free_embedding_model, load_embedding_model

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
