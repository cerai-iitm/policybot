# services/pdf_processor.py
import asyncio
import logging
import os
import uuid
import warnings
from pathlib import Path
from typing import AsyncGenerator, List, Optional

logger = logging.getLogger(__name__)

import numpy as np
import pymupdf
from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client.http.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_config
from app.prompts import COMBINE_PROMPT
from db.models.pdf import PDF
from db.models.notebook import Notebook
from db.models.pdf_suggested_query import PDFSuggestedQuery
from providers.embedding.factory import get_embedding
from providers.llm.factory import get_llm
from services.qdrant_client import get_qdrant_client
from services.suggested_queries import generate_suggested_queries

warnings.filterwarnings("ignore")


class PDFProcessor:
    def __init__(self) -> None:
        self.config = get_config()

    async def process_pdf(
        self, pdf_id: int, db: AsyncSession
    ) -> AsyncGenerator[str, None]:
        # Load PDF record
        result = await db.execute(select(PDF).where(PDF.id == pdf_id))
        pdf = result.scalar_one_or_none()
        if not pdf:
            yield "Error: PDF not found"
            return

        # If already fully processed, nothing to do.
        if pdf.processing_status == "complete":
            yield "Document ready"
            yield "done"
            return

        yield "Checking for existing embeddings..."
        embeddings_exist = False
        try:
            embeddings_exist = await self._check_existing_embeddings(
                pdf.stored_filename
            )
        except Exception:
            logger.exception("Error checking existing embeddings, assuming none exist")
            embeddings_exist = False

        docs = None

        # --- Embeddings stage (skip if already recorded in DB) ---
        if pdf.processing_status != "embeddings_complete":
            # If embeddings already exist in Qdrant, mark stage complete in DB
            if embeddings_exist:
                yield "Embeddings ready"
                pdf.processing_status = "embeddings_complete"
                db.add(pdf)
                await db.commit()
                # extract text for summary generation
                docs = await asyncio.to_thread(self._extract_text_from_pdf, pdf)
                if not docs:
                    yield "Error: Failed to extract text"
                    return
            else:
                # Perform full embedding pipeline and only mark embeddings_complete after success
                yield "Extracting text..."
                docs = await asyncio.to_thread(self._extract_text_from_pdf, pdf)
                if not docs:
                    yield "Error: Failed to extract text"
                    return

                yield "Creating chunks..."
                split_docs = await asyncio.to_thread(self._run_splitter, docs)
                if not split_docs:
                    yield "Error: Failed to split documents"
                    return

                yield "Processing embeddings..."
                embeddings = await self._embed_docs(split_docs)
                if embeddings is None:
                    yield "Error: Failed to generate embeddings"
                    return

                yield "Embeddings saved"
            try:
                await self._store_embeddings(
                    split_docs, embeddings, pdf.stored_filename, pdf.original_filename
                )
            except Exception:
                logger.exception(
                    "Error storing embeddings for stored_filename %s",
                    pdf.stored_filename,
                )
                yield "Error: Failed to store embeddings"
                return

            # Only mark embeddings_complete after successful upsert
            pdf.processing_status = "embeddings_complete"
            db.add(pdf)
            await db.commit()

        else:
            # embeddings already marked complete in DB; ensure we have text for summary
            yield "Reading document..."
            docs = await asyncio.to_thread(self._extract_text_from_pdf, pdf)
            if not docs:
                yield "Error: Failed to extract text"
                return

        # --- Summary stage (skip if already complete) ---
        if pdf.processing_status != "complete":
            # If a summary already exists on the row, treat as complete
            if pdf.summary:
                pdf.processing_status = "complete"
                db.add(pdf)
                await db.commit()
                yield "Summary ready"
                yield "done"
                return

        yield "Generating summary..."
        summary_text = await self._create_summary(docs, pdf.original_filename)

        if summary_text:
            pdf.summary = summary_text
            pdf.processing_status = "complete"
            db.add(pdf)
            await db.commit()
            yield "Summary complete"

            # Auto-generate notebook title if first complete PDF + default title
            try:
                check_result = await db.execute(
                    select(PDF).where(
                        PDF.notebook_id == pdf.notebook_id,
                        PDF.processing_status == "complete",
                    )
                )
                existing_pdfs = check_result.scalars().all()

                # Only update if this is the first complete PDF and title is default
                if len(existing_pdfs) == 1 and pdf.id == existing_pdfs[0].id:
                    notebook = await db.get(Notebook, pdf.notebook_id)
                    if notebook and notebook.title == "Untitled":
                        from services.rag import generate_notebook_title

                        new_title = await generate_notebook_title(pdf.summary)
                        notebook.title = new_title
                        await db.commit()
                        yield f'data: {{"type": "notebook_title", "title": "{new_title}"}}\n\n'
            except Exception as e:
                logger.exception("Error generating notebook title")

            # --- Suggested Queries stage ---
            yield "Creating suggestions..."
            queries_created = await self._generate_suggested_queries(
                pdf.summary, pdf_id, db
            )
            if queries_created:
                yield "Suggestions ready"
            else:
                yield "Suggestions ready"
        else:
            # Summary failed; do not change processing_status so worker can retry
            yield "Error: Failed to create summary"
            return

        yield "done"

    def _extract_text_from_pdf(self, pdf: PDF) -> Optional[List[Document]]:
        # Files are stored in backend/uploads/ relative to app root
        import os

        app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = Path(app_root) / "uploads" / pdf.file_path
        if not file_path.exists():
            return None

        try:
            pdf_doc = pymupdf.open(str(file_path))
            documents = []

            for page_num in range(len(pdf_doc)):
                page = pdf_doc.load_page(page_num)
                raw_text = page.get_text("text")
                text = str(raw_text).strip()

                if text:
                    metadata = {
                        "page_number": page_num + 1,
                        "source": pdf.original_filename,
                    }
                    doc = Document(page_content=text, metadata=metadata)
                    documents.append(doc)

            pdf_doc.close()
            return documents if documents else None
        except Exception:
            return None

    def _run_splitter(self, docs: List[Document]) -> Optional[List[Document]]:
        try:
            embedder = get_embedding()
            splitter = SemanticChunker(
                embeddings=embedder,
                breakpoint_threshold_type=self.config.breakpoint_threshold_type,
                breakpoint_threshold_amount=self.config.breakpoint_threshold_amount,
            )
            return splitter.split_documents(docs)
        except Exception:
            return None

    async def _embed_docs(self, docs: List[Document]) -> Optional[np.ndarray]:
        try:
            embedder = get_embedding()
            texts = [doc.page_content for doc in docs]

            # Prefer async embedding if available, but fall back to sync embedding
            # if the async call fails (e.g. proxy/async client issues).
            if hasattr(embedder, "aembed_documents"):
                try:
                    all_embeddings = []
                    for i in range(0, len(texts), 128):
                        batch = texts[i : i + 128]
                        batch_embeddings = await embedder.aembed_documents(batch)
                        all_embeddings.extend(batch_embeddings)
                    return np.array(all_embeddings, dtype=np.float32)
                except Exception:
                    # Async embedding failed — fall back to sync embed_documents
                    all_embeddings = []
                    for i in range(0, len(texts), 128):
                        batch = texts[i : i + 128]
                        emb = await asyncio.to_thread(embedder.embed_documents, batch)
                        all_embeddings.extend(emb)
                    return np.array(all_embeddings, dtype=np.float32)
            else:
                all_embeddings = []
                for i in range(0, len(texts), 128):
                    batch = texts[i : i + 128]
                    emb = await asyncio.to_thread(embedder.embed_documents, batch)
                    all_embeddings.extend(emb)
                return np.array(all_embeddings, dtype=np.float32)
        except Exception:
            return None

    async def _store_embeddings(
        self, docs: List[Document], embeddings: np.ndarray, stored_filename: str, original_filename: str
    ) -> None:
        client = get_qdrant_client()
        try:
            try:
                await client.get_collection(self.config.q_collection_name)
            except Exception:
                await client.create_collection(
                    collection_name=self.config.q_collection_name,
                    vectors_config=VectorParams(
                        size=embeddings.shape[1], distance=Distance.COSINE
                    ),
                )

            points = [
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embeddings[i].tolist(),
                    payload={
                        "text": docs[i].page_content,
                        "stored_filename": stored_filename,
                        "original_filename": original_filename,
                        "page_number": docs[i].metadata.get("page_number"),
                    },
                )
                for i in range(len(docs))
            ]

            await client.upsert(
                collection_name=self.config.q_collection_name, points=points
            )
        finally:
            await client.close()

    async def _check_existing_embeddings(self, stored_filename: str) -> bool:
        client = get_qdrant_client()
        try:
            filter_ = Filter(
                must=[
                    FieldCondition(
                        key="stored_filename", match=MatchValue(value=stored_filename)
                    )
                ]
            )
            result = await client.scroll(
                collection_name=self.config.q_collection_name,
                limit=1,
                scroll_filter=filter_,
            )
            return bool(result[0])
        except Exception:
            return False
        finally:
            await client.close()

    async def _create_summary(
        self, docs: List[Document], source_name: str
    ) -> Optional[str]:
        try:
            text = "\n".join([doc.page_content for doc in docs])

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=8000, chunk_overlap=200
            )
            splits = splitter.split_text(text)
            documents = [Document(page_content=t) for t in splits]

            llm = get_llm()
            from langchain_classic.chains.summarize import load_summarize_chain

            chain = load_summarize_chain(
                llm, chain_type="map_reduce", combine_prompt=COMBINE_PROMPT
            )
            result = await asyncio.to_thread(
                chain.invoke, {"input_documents": documents}
            )

            return result["output_text"]
        except Exception:
            logger.exception("Error creating summary")
            return None

    async def _generate_suggested_queries(
        self, summary: str, pdf_id: int, db: AsyncSession
    ) -> bool:
        """Generate and store suggested queries for a PDF."""
        try:
            queries = await generate_suggested_queries(summary)
            if not queries:
                return False

            # Store each query in database
            for i, query_text in enumerate(queries):
                suggested_query = PDFSuggestedQuery(
                    pdf_id=pdf_id,
                    query_text=query_text,
                    order_index=i,
                )
                db.add(suggested_query)
            await db.commit()
            return True
        except Exception:
            logger.exception("Error in _generate_suggested_queries")
            await db.rollback()
            return False

    async def delete_embeddings(self, stored_filename: str) -> bool:
        client = get_qdrant_client()
        try:
            filter_ = Filter(
                must=[
                    FieldCondition(
                        key="stored_filename", match=MatchValue(value=stored_filename)
                    )
                ]
            )
            from qdrant_client.http.models import FilterSelector

            await client.delete(
                collection_name=self.config.q_collection_name,
                points_selector=FilterSelector(filter=filter_),
            )
            return True
        except Exception:
            return False
        finally:
            await client.close()
