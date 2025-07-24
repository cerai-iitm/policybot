from collections import defaultdict
from typing import List, Optional

import chromadb
import numpy as np
from FlagEmbedding import FlagReranker

from src.config import cfg
from src.logger import logger
from src.rag.LLM_interface import LLM_Interface
from src.util import free_embedding_model, load_embedding_model


class Retriever:
    def __init__(
        self,
        interface: LLM_Interface,
        top_k: int = 5,
    ) -> None:
        self.chroma_client = chromadb.PersistentClient(path=cfg.DB_DIR)
        self.collection = self.chroma_client.get_or_create_collection(
            name=cfg.COLLECTION_NAME
        )
        self.top_k = top_k
        self.interface = interface
        self.reranker = FlagReranker(cfg.RERANKING_MODEL_NAME, use_fp16=True)

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
            scores = self.reranker.compute_score([(query, chunk) for chunk in chunks])
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

    def retrieve(
        self, query: str, file_name: str, top_k: Optional[int] = None
    ) -> List[str]:
        if top_k is None:
            top_k = self.top_k

        try:
            embedding_model, device = load_embedding_model("cpu")
            logger.info("Generating rewritten queries for better retrieval")
            rewritten_queries = self.interface.generate_rewritten_queries(query=query)
            logger.debug(f"Debugging query rewriting: {rewritten_queries}")

            logger.info("Generating query embeddings")
            query_embeddings = [
                embedding_model.embed_query(rewritten_query)
                for rewritten_query in rewritten_queries
            ]
            query_embeddings = np.array(query_embeddings, dtype=np.float32)
            free_embedding_model(embedding_model, device)

            logger.info("Retrieving relevant chunks from the database")
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=top_k,
                where={"source": str(file_name)},
                include=["documents", "metadatas", "distances"],
            )
            logger.info("Performing rank fusion on retrieved results")
            ranked_chunk_ids = self.reciprocal_rank_fusion(results["ids"], k=top_k)

            id_to_doc = {}
            documents = results.get("documents") or []
            for id_list, doc_list in zip(results["ids"], documents):
                for chunk_id, doc in zip(id_list, doc_list):
                    if chunk_id not in id_to_doc:
                        id_to_doc[chunk_id] = doc
            filtered_chunks = [
                id_to_doc[chunk_id]
                for chunk_id in ranked_chunk_ids
                if chunk_id in id_to_doc
            ]

            reranked_chunks = self.rerank_chunks(query, filtered_chunks)
            return reranked_chunks
        except Exception as e:
            logger.error(f"Error retrieving data: {e}")
            return []


if __name__ == "__main__":

    def format_chunks_to_text(chunks: List[str]) -> str:
        try:
            formatted_chunks = []
            for chunk in chunks:
                formatted_chunks.append(f"{cfg.CHUNK_PREFIX}{chunk}")

            content = cfg.CHUNK_SEPARATOR.join(formatted_chunks)
            return f"{cfg.RESPONSE_START}{content}{cfg.RESPONSE_END}"

        except Exception as e:
            logger.error(f"Error formatting chunks to text: {e}")
            return f"{cfg.RESPONSE_START}{cfg.RESPONSE_END}"

    import sys

    if len(sys.argv) != 5:
        result = format_chunks_to_text([])
        print(result)
        sys.exit(1)

    file_name = sys.argv[1]
    query = sys.argv[2]
    top_k = int(sys.argv[3])
    output_file = sys.argv[4]

    try:
        llm_interface = LLM_Interface()
        retriever = Retriever(llm_interface)
        chunks = retriever.retrieve(query, file_name, top_k)

        result_text = format_chunks_to_text(chunks)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result_text)

    except Exception as e:
        error_result = format_chunks_to_text([])
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(error_result)
        except:
            print(error_result)
        sys.exit(1)
