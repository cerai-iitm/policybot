import asyncio
import os
import uuid
import warnings
from typing import AsyncGenerator, List, Optional

import numpy as np
import pymupdf
from langchain_classic.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import (Distance, FieldCondition, Filter,
                                       FilterSelector, MatchValue, PointStruct,
                                       VectorParams)
from sqlalchemy.ext.asyncio import AsyncSession
from transformers import logging as hf_logging

from src.config import cfg
from src.logger import logger
from src.rag import LLM_Interface
from src.schema.source_summaries_crud import (add_source_summary,
                                              get_summary_by_source_name)
from src.util import free_embedding_model, load_embedding_model

warnings.filterwarnings("ignore", category=UserWarning, module="transformers")
hf_logging.set_verbosity_error()


class PDFProcessor:
    def __init__(self) -> None:
        self.interface = LLM_Interface()

    async def process_pdf(
        self, file_name: str, db: Optional[AsyncSession] = None
    ) -> AsyncGenerator[str, None]:
        """
        Process a PDF and yield status updates.

        Accepts an optional AsyncSession `db`. When provided, source summaries
        will be looked up and persisted using the async CRUD functions.
        """
        logger.info(f"Processing PDF file: {file_name}")
        yield "Starting PDF processing..."
        await asyncio.sleep(0)

        yield "Checking for existing embeddings..."
        await asyncio.sleep(0)
        embeddings_exist = await self._check_existing_embeddings(file_name)

        docs = None
        if embeddings_exist:
            yield "Embeddings already exist. Skipping to summary generation..."
            # Extract text for summary generation only
            yield "Extracting text from PDF for summary..."
            await asyncio.sleep(0)
            docs = await asyncio.to_thread(self._extract_text_from_pdf, file_name)
            if not docs:
                yield "Error: Failed to extract text."
                return
        else:
            yield "Embeddings not found. Starting full processing..."
            yield "Extracting text from PDF..."
            await asyncio.sleep(0)
            docs = await asyncio.to_thread(self._extract_text_from_pdf, file_name)
            if not docs:
                yield "Error: Failed to extract text."
                return

            yield "Running splitter for creating chunks..."
            await asyncio.sleep(0)
            split_docs = await asyncio.to_thread(self._run_splitter, docs, file_name)
            if not split_docs:
                yield "Error: Failed to split documents."
                return

            yield "Embedding chunks..."
            await asyncio.sleep(0)
            embeddings = await asyncio.to_thread(
                self._embed_docs, split_docs, file_name
            )
            if embeddings is None:
                yield "Error: Failed to generate embeddings."
                return
            logger.info(
                f"Generated embeddings shape: {embeddings.shape} for {file_name}."
            )

            yield "Saving embeddings to database..."
            await asyncio.sleep(0)
            await self._store_embeddings(split_docs, embeddings, file_name)
            logger.info(
                f"Successfully processed and stored embeddings for {file_name}."
            )

        yield "Creating summary..."
        await asyncio.sleep(0)
        # _create_summary is now async and will perform async DB CRUD when a session is provided.
        summary_result = await self._create_summary(docs, file_name, db=db)
        if summary_result:
            yield "Summary created and saved."
        else:
            yield "Error: Failed to create summary."

        yield "PDF processing complete."
        yield "done"

    def _split_text_by_tokens(self, text: str, tokens_per_chunk: int) -> List[str]:
        words = text.split()
        words_per_chunk = int(tokens_per_chunk / 1.33)
        chunks = []
        for i in range(0, len(words), words_per_chunk):
            chunk = " ".join(words[i : i + words_per_chunk])
            chunks.append(chunk)
        return chunks

    async def _create_summary(
        self, docs: List[Document], file_name: str, db: Optional[AsyncSession]
    ) -> Optional[tuple[str, str]]:
        """
        Create a summary for the provided documents.

        - If `db` (AsyncSession) is provided, use async CRUD to check for and store summaries.
        - If a summary already exists in the DB, return it and skip generation.
        - Uses an async `arun` on the map-reduce summarize chain when available.
        """
        logger.info(f"Creating a summary for {file_name}.")
        try:
            # Check for existing summary in DB if session supplied
            existing_summary = None
            if db is not None:
                existing_summary = await get_summary_by_source_name(
                    db, os.path.basename(file_name)
                )
            else:
                logger.debug(
                    "No AsyncSession provided to _create_summary; will not read/write DB."
                )

            if existing_summary:
                logger.info(
                    f"Summary already exists for {file_name}. Skipping sumamary creation."
                )
                return file_name, existing_summary

            # Build a single document and chunk it for summarization
            text = "\n".join([doc.page_content for doc in docs])
            doc = Document(page_content=text, metadata={"source": file_name})
            splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=0)
            recursive_docs = splitter.split_documents([doc])
            logger.info(
                f"Split text into {len(recursive_docs)} chunks for summarization."
            )

            # Create the summarization chain and prefer async execution if available
            chain = load_summarize_chain(self.interface.llm, chain_type="map_reduce")
            summary_result = None
            if hasattr(chain, "arun"):
                summary_result = await chain.arun({"input_documents": recursive_docs})
            else:
                # Fallback to running the synchronous invoke in a thread
                summary_result = await asyncio.to_thread(
                    chain.invoke, {"input_documents": recursive_docs}
                )

            # Extract text from chain result
            if isinstance(summary_result, dict):
                summary_text = summary_result.get("output_text", str(summary_result))
            else:
                summary_text = str(summary_result)

            # Persist the summary using async CRUD if session supplied
            if db is not None:
                await add_source_summary(
                    db,
                    source_name=os.path.basename(file_name),
                    summary=summary_text,
                )
                logger.info("Summary created and saved to database.")
            else:
                logger.info("Summary created but not saved (no DB session provided).")

            return file_name, summary_text

        except Exception as e:
            logger.error(f"Error creating summary for {file_name}: {e}")
            return

    def _extract_text_from_pdf(self, file_name: str) -> Optional[List[Document]]:
        file_path = os.path.join(cfg.DATA_DIR, file_name)
        logger.info(f"Extracting text from PDF file: {file_path}")

        if not os.path.exists(file_path):
            logger.error(f"PDF file not found: {file_path}")
            return None

        try:
            pdf_doc = pymupdf.open(file_path)
            documents = []

            for page_num in range(len(pdf_doc)):
                # Use load_page by index to avoid relying on iteration protocol of
                # the pymupdf Document (which caused static typing/analysis issues).
                page = pdf_doc.load_page(page_num)
                # Coerce the raw page text to str before calling .strip() so static
                # analysis and runtime are robust against non-string return types.
                raw_text = page.get_text("text")
                text = str(raw_text).strip()

                metadata = {
                    "page_number": page_num + 1,
                    "source": file_name,
                }

                doc = Document(page_content=text, metadata=metadata)
                documents.append(doc)
            pdf_doc.close()

            if not documents:
                logger.info(f"No text found in PDF {file_name}.")
                return None
            logger.info(f"Extracted {len(documents)} page documents from {file_name}.")
            return documents

        except Exception as e:
            logger.error(f"Error processing PDF {file_name}: {e}")
            return None

    async def _check_existing_embeddings(self, file_name: str) -> bool:
        logger.info(f"Checking existing embeddings for {file_name}...")
        try:
            client = AsyncQdrantClient(host=cfg.QDRANT_HOST, port=cfg.QDRANT_PORT)
            # Use scroll to find any point with the given source
            filter_ = Filter(
                must=[FieldCondition(key="source", match=MatchValue(value=file_name))]
            )
            result = await client.scroll(
                collection_name=cfg.COLLECTION_NAME,
                limit=1,
                scroll_filter=filter_,
            )
            await client.close()
            if result and result[0]:
                logger.info(
                    f"Document embeddings already exist in Qdrant for {file_name}."
                )
                return True
            logger.info(f"No existing embeddings found in Qdrant for {file_name}.")
            return False
        except Exception as e:
            logger.error(f"Error checking embeddings in Qdrant: {e}")
            return False

    def _run_splitter(
        self, docs: List[Document], file_name: str
    ) -> Optional[List[Document]]:
        logger.info(f"Running splitter on {len(docs)} documents for {file_name}.")
        try:
            embedding_model, device = load_embedding_model()
            splitter = SemanticChunker(
                embeddings=embedding_model,
                breakpoint_threshold_type=cfg.BREAKPOINT_THRESHOLD_TYPE,
                breakpoint_threshold_amount=cfg.BREAKPOINT_THRESHOLD_AMOUNT,
            )
            split_docs = splitter.split_documents(docs)
            free_embedding_model(embedding_model, device)
            logger.info(
                f"Split {len(docs)} page documents into {len(split_docs)} chunks for {file_name}."
            )
            return split_docs

        except Exception as e:
            logger.error(f"Error processing PDF {file_name} with splitter: {e}")
            return None

    def _embed_docs(self, docs: List[Document], file_name: str) -> Optional[np.ndarray]:
        try:
            logger.info(f"Embedding {len(docs)} chunks for {file_name}.")
            embedding_model, device = load_embedding_model()
            all_embeddings = []

            for i, doc in enumerate(docs):
                try:
                    text = [doc.page_content]
                    embedding = embedding_model.embed_documents(text)
                    all_embeddings.extend(embedding)

                    if device == "cuda":
                        import torch

                        torch.cuda.empty_cache()

                except Exception as e:
                    logger.error(f"Error embedding document {i}: {e}")
                    return None
            embeddings = np.array(all_embeddings, dtype=np.float32)
            free_embedding_model(embedding_model, device)
            logger.info(f"Generated embeddings for {len(all_embeddings)} chunks.")
            return embeddings if len(all_embeddings) > 0 else None
        except Exception as e:
            logger.error(f"Error embedding documents: {e}")
            return None

    async def _store_embeddings(
        self, docs: List[Document], embeddings: np.ndarray, file_name: str
    ) -> None:
        try:
            logger.info(f"Saving embeddings to db for {file_name}")
            client = AsyncQdrantClient(host=cfg.QDRANT_HOST, port=cfg.QDRANT_PORT)

            try:
                await client.get_collection(cfg.COLLECTION_NAME)
                logger.info(f"Collection {cfg.COLLECTION_NAME} already exists")
            except Exception:
                await client.create_collection(
                    collection_name=cfg.COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=embeddings.shape[1], distance=Distance.COSINE
                    ),
                )
                logger.info(f"Created new collection {cfg.COLLECTION_NAME}")

            points = [
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embeddings[i].tolist(),
                    payload={
                        "text": docs[i].page_content,
                        "source": file_name,
                        "page_number": docs[i].metadata.get("page_number"),
                    },
                )
                for i in range(len(docs))
            ]
            logger.info(f"Stored embeddings for {len(docs)} chunks.")

            await client.upsert(collection_name=cfg.COLLECTION_NAME, points=points)
            await client.close()

        except Exception as e:
            logger.error(f"Error storing embeddings: {e}")

    async def delete_embeddings(self, source_name: str) -> bool:
        client = None
        try:
            logger.info(
                f"Starting Qdrant embeddings deletion for source: {source_name}"
            )
            logger.debug(f"Connecting to Qdrant at {cfg.QDRANT_HOST}:{cfg.QDRANT_PORT}")
            client = AsyncQdrantClient(host=cfg.QDRANT_HOST, port=cfg.QDRANT_PORT)

            # Create filter for the source
            filter_ = Filter(
                must=[FieldCondition(key="source", match=MatchValue(value=source_name))]
            )
            logger.debug(f"Created filter for source: {source_name}")

            # Delete all points matching the filter
            logger.info(
                f"Deleting points from collection '{cfg.COLLECTION_NAME}' for source: {source_name}"
            )
            result = await client.delete(
                collection_name=cfg.COLLECTION_NAME,
                points_selector=FilterSelector(filter=filter_),
            )
            logger.debug(f"Qdrant delete operation result: {result}")

            logger.info(
                f"Successfully deleted embeddings for {source_name} from Qdrant"
            )
            return True
        except Exception as e:
            logger.error(
                f"Error deleting embeddings for {source_name}: {type(e).__name__} - {e}",
                exc_info=True,
            )
            return False
        finally:
            if client:
                try:
                    await client.close()
                    logger.debug(f"Closed Qdrant client connection for {source_name}")
                except Exception as close_error:
                    logger.warning(f"Error closing Qdrant client: {close_error}")


if __name__ == "__main__":
    pass
