from typing import List, Optional

import chromadb
import numpy as np

from src.config import cfg
from src.logger import logger
from src.util import free_embedding_model, load_embedding_model


class Retriever:
    def __init__(self, top_k: int = 5):
        self.chroma_client = chromadb.PersistentClient(path=cfg.DB_DIR)
        self.collection = self.chroma_client.get_or_create_collection(
            name=cfg.COLLECTION_NAME
        )
        self.top_k = top_k

    def retrieve(
        self, query: str, file_name: str, top_k: Optional[int] = None
    ) -> List[str]:
        logger.info(f"Retrieving top {top_k} chunks for query: {query}")

        if top_k is None:
            top_k = self.top_k

        try:
            embedding_model, device = load_embedding_model("cpu")
            query_embedding = np.array(
                embedding_model.embed_query(query), dtype=np.float32
            )
            free_embedding_model(embedding_model, device)

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"source": str(file_name)},
                include=["documents", "metadatas", "distances"],
            )

            documents = results.get("documents", [])
            if documents is None or len(documents) == 0:
                logger.info(
                    f"No documents found for file '{file_name}' and query '{query}'"
                )
                return []

            flattened_docs = documents[0] if documents else []
            logger.info(f"Retrieved {len(flattened_docs)} chunks for query")
            return flattened_docs

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
        retriever = Retriever()
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
