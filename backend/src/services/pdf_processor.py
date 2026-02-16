import asyncio
import os
import uuid
import warnings
from typing import AsyncGenerator, List, Optional, Union

import numpy as np
import pymupdf
from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
    PointStruct,
    VectorParams,
)
from sqlalchemy.ext.asyncio import AsyncSession
from transformers import logging as hf_logging

from src.core import cfg, free_embedding_model, load_embedding_model, logger
from src.db.crud import (
    add_source_summary,
    get_summary_by_source_name,
    update_pdf_status,
)
from src.services import LLM_Interface

warnings.filterwarnings("ignore", category=UserWarning, module="transformers")
hf_logging.set_verbosity_error()


class PDFProcessor:
    def __init__(self) -> None:
        self.interface = LLM_Interface()

    async def process_pdf(
        self,
        file_name: str,
        pdf_id: Optional[int] = None,
        db: Optional[AsyncSession] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Process a PDF and yield status updates.

        Args:
            file_name: Name of the PDF file
            pdf_id: ID of the PDF record in database (for status updates)
            db: AsyncSession for database operations
        """
        logger.info(f"Processing PDF file: {file_name} (pdf_id: {pdf_id})")
        yield "Starting PDF processing..."
        await asyncio.sleep(0)

        # Update status to 'processing' if we have pdf_id and db
        if pdf_id and db:
            await update_pdf_status(db, pdf_id, "processing")
            logger.info(f"Updated status to 'processing' for pdf_id: {pdf_id}")

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

            # Process embeddings with progress updates
            embeddings = None
            async for update in self._embed_docs(split_docs, file_name):
                if isinstance(update, str):
                    # Progress update - yield it to user
                    if update.startswith("Embedding:") or update.startswith("Error:"):
                        yield update
                elif isinstance(update, np.ndarray):
                    # Final result
                    embeddings = update
                elif update is None:
                    # Error case
                    yield "Error: Failed to generate embeddings."
                    return

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

            # Update status to 'embeddings_complete'
            if pdf_id and db:
                await update_pdf_status(db, pdf_id, "embeddings_complete")
                logger.info(
                    f"Updated status to 'embeddings_complete' for pdf_id: {pdf_id}"
                )

        # Update status to 'summary_generation' before creating summary
        if pdf_id and db:
            await update_pdf_status(db, pdf_id, "summary_generation")
            logger.info(f"Updated status to 'summary_generation' for pdf_id: {pdf_id}")

        yield "Creating summary..."
        await asyncio.sleep(0)
        summary_result = await self._create_summary(docs, file_name, db=db)
        if summary_result:
            yield "Summary created and saved."
            # Update status to 'complete'
            if pdf_id and db:
                await update_pdf_status(db, pdf_id, "complete")
                logger.info(f"Updated status to 'complete' for pdf_id: {pdf_id}")
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
        """Create summary using hierarchical batch reduction with 8:1 compression ratio."""
        from openai import AsyncOpenAI
        from src.core.prompts import (
            MAP_SUMMARIZATION_PROMPT,
            REDUCE_SUMMARIZATION_PROMPT,
            FINAL_SUMMARY_PROMPT,
        )

        logger.info(f"Creating a summary for {file_name}.")

        try:
            # Check for existing summary
            if db is not None:
                existing_summary = await get_summary_by_source_name(
                    db, os.path.basename(file_name)
                )
                if existing_summary:
                    logger.info(f"Summary already exists for {file_name}.")
                    return file_name, existing_summary

            # Chunk the document
            text = "\n".join([doc.page_content for doc in docs])
            doc = Document(page_content=text, metadata={"source": file_name})
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=8000, chunk_overlap=200
            )
            recursive_docs = splitter.split_documents([doc])
            logger.info(
                f"Split text into {len(recursive_docs)} chunks for summarization."
            )

            # Initialize OpenAI client
            client = AsyncOpenAI(
                base_url=cfg.VLLM_LLM_URL, api_key=cfg.VLLM_LLM_API_KEY
            )

            # MAP PHASE: Summarize chunks in batches of max 8
            async def summarize_chunk(chunk: Document) -> str:
                prompt = MAP_SUMMARIZATION_PROMPT.format(text=chunk.page_content[:8000])
                response = await client.chat.completions.create(
                    model=cfg.VLLM_LLM_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,  # Each summary ~1000 tokens
                    temperature=0.7,
                )
                return response.choices[0].message.content

            # Process chunks in batches of 8
            chunk_summaries = []
            batch_size = 8
            for i in range(0, len(recursive_docs), batch_size):
                batch = recursive_docs[i : i + batch_size]
                batch_results = await asyncio.gather(
                    *[summarize_chunk(doc) for doc in batch]
                )
                chunk_summaries.extend(batch_results)
                logger.info(
                    f"Processed batch {i // batch_size + 1}/{(len(recursive_docs) - 1) // batch_size + 1}"
                )

            logger.info(f"Generated {len(chunk_summaries)} chunk summaries.")

            # REDUCE PHASE: Hierarchical batch reduction with 8:1 ratio
            current_summaries = chunk_summaries.copy()
            reduce_depth = 0

            while True:
                total_tokens = sum(len(s.split()) for s in current_summaries)
                logger.info(
                    f"Reduce depth {reduce_depth}: {len(current_summaries)} summaries, ~{total_tokens} tokens"
                )

                # If total is under 8000 tokens, we can do final reduce
                if total_tokens <= 8000 and len(current_summaries) <= 8:
                    break

                # Batch summaries into groups of max 8000 tokens
                batches = []
                current_batch = []
                current_batch_tokens = 0

                for summary in current_summaries:
                    summary_tokens = len(summary.split())
                    # If adding this summary exceeds 8000 tokens, start new batch
                    if current_batch_tokens + summary_tokens > 8000 and current_batch:
                        batches.append(current_batch)
                        current_batch = [summary]
                        current_batch_tokens = summary_tokens
                    else:
                        current_batch.append(summary)
                        current_batch_tokens += summary_tokens

                # Add final batch
                if current_batch:
                    batches.append(current_batch)

                logger.info(
                    f"Created {len(batches)} batches for reduce depth {reduce_depth}"
                )

                # Reduce each batch to ~1000 tokens
                new_summaries = []
                for batch_idx, batch in enumerate(batches):
                    combined_text = "\n\n---\n\n".join(batch)
                    reduce_prompt = REDUCE_SUMMARIZATION_PROMPT.format(
                        text=combined_text
                    )

                    reduce_response = await client.chat.completions.create(
                        model=cfg.VLLM_LLM_MODEL,
                        messages=[{"role": "user", "content": reduce_prompt}],
                        max_tokens=1000,  # Each reduce produces ~1000 tokens
                        temperature=0.7,
                    )
                    new_summaries.append(reduce_response.choices[0].message.content)
                    logger.info(
                        f"Reduced batch {batch_idx + 1}/{len(batches)} at depth {reduce_depth}"
                    )

                current_summaries = new_summaries
                reduce_depth += 1

            # FINAL REDUCE: Create final 500-700 word summary
            combined_text = "\n\n---\n\n".join(current_summaries)
            final_prompt = FINAL_SUMMARY_PROMPT.format(text=combined_text)

            final_response = await client.chat.completions.create(
                model=cfg.VLLM_LLM_MODEL,
                messages=[{"role": "user", "content": final_prompt}],
                max_tokens=2000,
                temperature=0.7,
            )

            summary_text = final_response.choices[0].message.content
            logger.info(
                f"Generated final summary for {file_name} after {reduce_depth} reduction levels."
            )

            # Persist summary
            if db is not None:
                await add_source_summary(
                    db,
                    source_name=os.path.basename(file_name),
                    summary=summary_text,
                )
                logger.info("Summary created and saved to database.")

            return file_name, summary_text

        except Exception as e:
            logger.error(f"Error creating summary for {file_name}: {e}")
            return None

    def _extract_text_from_pdf(self, file_name: str) -> Optional[List[Document]]:
        # Try the provided path first (may be "nb_xxx/filename.pdf" or just "filename.pdf")
        file_path = os.path.join(cfg.DATA_DIR, file_name)
        logger.info(f"Extracting text from PDF file: {file_path}")

        if not os.path.exists(file_path):
            # Fallback: search DATA_DIR for a file with the same basename. This makes
            # processing resilient when callers pass only the basename while files
            # are saved under notebook subfolders.
            basename = os.path.basename(file_name)
            logger.info(
                f"PDF not found at path; searching for basename {basename} under {cfg.DATA_DIR}"
            )
            found = None
            for root, _, files in os.walk(cfg.DATA_DIR):
                if basename in files:
                    found = os.path.join(root, basename)
                    break
            if found:
                logger.info(f"Found PDF by searching: {found}")
                file_path = found
            else:
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

                # Use basename for the source field so Qdrant payloads are consistent
                # and independent of notebook folder layout.
                metadata = {
                    "page_number": page_num + 1,
                    "source": os.path.basename(file_name),
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
            source_name = os.path.basename(file_name)
            filter_ = Filter(
                must=[FieldCondition(key="source", match=MatchValue(value=source_name))]
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

    async def _embed_docs(
        self, docs: List[Document], file_name: str
    ) -> AsyncGenerator[Union[str, np.ndarray], None]:
        """Embed documents using vLLM async or local fallback with progress updates."""
        try:
            total_docs = len(docs)
            logger.info(f"Embedding {total_docs} chunks for {file_name}.")

            # Yield initial progress
            yield f"Embedding: Starting {total_docs} documents..."
            last_progress_time = asyncio.get_event_loop().time()

            if cfg.VLLM_EMBEDDING_ENABLED:
                # Use vLLM with progress tracking
                from src.services.vllm_embeddings import (
                    get_vllm_document_embeddings,
                )

                embeddings = await get_vllm_document_embeddings(
                    documents=docs, batch_size=128, max_concurrent=4
                )

                # Yield final progress
                yield f"Embedding: Complete ({total_docs}/{total_docs} documents, 100%)"
                yield embeddings
            else:
                # Local embedding with periodic progress
                all_embeddings = []
                for i, doc in enumerate(docs):
                    text = [doc.page_content]
                    embedding_model, device = load_embedding_model()
                    embedding = embedding_model.embed_documents(text)
                    all_embeddings.extend(embedding)
                    free_embedding_model(embedding_model, device)

                    # Update progress every ~5 seconds
                    current_time = asyncio.get_event_loop().time()
                    if current_time - last_progress_time >= 5.0 or i == len(docs) - 1:
                        progress_pct = int(((i + 1) / total_docs) * 100)
                        yield f"Embedding: {i + 1}/{total_docs} documents ({progress_pct}%)"
                        last_progress_time = current_time

                embeddings = np.array(all_embeddings, dtype=np.float32)
                yield embeddings

        except Exception as e:
            logger.error(f"Error embedding documents: {e}")
            yield "Error: Failed to generate embeddings."
            yield None

    def _embed_docs_local(
        self, docs: List[Document], file_name: str
    ) -> Optional[np.ndarray]:
        """Local HuggingFace embedding fallback (original implementation)."""
        try:
            logger.info(f"Embedding {len(docs)} chunks locally for {file_name}.")
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
                    free_embedding_model(embedding_model, device)
                    return None

            embeddings = np.array(all_embeddings, dtype=np.float32)
            free_embedding_model(embedding_model, device)
            logger.info(f"Generated {len(all_embeddings)} local embeddings.")
            return embeddings if len(all_embeddings) > 0 else None

        except Exception as e:
            logger.error(f"Error in local embedding: {e}")
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
