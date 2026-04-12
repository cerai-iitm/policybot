# services/pdf_processor.py
import asyncio
import os
import uuid
import warnings
from pathlib import Path
from typing import AsyncGenerator, List, Optional

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
from db.models.pdf import PDF
from providers.embedding.factory import get_embedding
from providers.llm.factory import get_llm
from services.qdrant_client import get_qdrant_client

warnings.filterwarnings("ignore")


class PDFProcessor:
    def __init__(self) -> None:
        self.config = get_config()

    async def process_pdf(
        self, pdf_id: int, db: AsyncSession
    ) -> AsyncGenerator[str, None]:
        result = await db.execute(select(PDF).where(PDF.id == pdf_id))
        pdf = result.scalar_one_or_none()
        if not pdf:
            yield "Error: PDF not found"
            return

        yield "Starting PDF processing..."
        pdf.processing_status = "processing"
        await db.commit()

        yield "Checking for existing embeddings..."
        embeddings_exist = await self._check_existing_embeddings(pdf.id)

        docs = None
        if embeddings_exist:
            yield "Embeddings already exist. Extracting text for summary..."
            docs = await asyncio.to_thread(self._extract_text_from_pdf, pdf)
            if not docs:
                yield "Error: Failed to extract text"
                return
        else:
            yield "Extracting text from PDF..."
            docs = await asyncio.to_thread(self._extract_text_from_pdf, pdf)
            if not docs:
                yield "Error: Failed to extract text"
                return

            yield "Creating chunks..."
            split_docs = await asyncio.to_thread(self._run_splitter, docs)
            if not split_docs:
                yield "Error: Failed to split documents"
                return

            yield "Generating embeddings..."
            embeddings = await self._embed_docs(split_docs)
            if embeddings is None:
                yield "Error: Failed to generate embeddings"
                return

            yield "Storing embeddings..."
            await self._store_embeddings(split_docs, embeddings, pdf.id)

        pdf.processing_status = "embeddings_complete"
        await db.commit()

        yield "Generating summary..."
        summary = await self._create_summary(docs, pdf.original_filename)
        if summary:
            pdf.summary = summary
            pdf.processing_status = "complete"
            await db.commit()
            yield "Summary created"
        else:
            yield "Error: Failed to create summary"

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
        self, docs: List[Document], embeddings: np.ndarray, pdf_id: int
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
                        "pdf_id": pdf_id,
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

    async def _check_existing_embeddings(self, pdf_id: int) -> bool:
        client = get_qdrant_client()
        try:
            filter_ = Filter(
                must=[FieldCondition(key="pdf_id", match=MatchValue(value=pdf_id))]
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

            chain = load_summarize_chain(llm, chain_type="map_reduce")
            result = await asyncio.to_thread(
                chain.invoke, {"input_documents": documents}
            )

            return result["output_text"]
        except Exception:
            return None

    async def delete_embeddings(self, pdf_id: int) -> bool:
        client = get_qdrant_client()
        try:
            filter_ = Filter(
                must=[FieldCondition(key="pdf_id", match=MatchValue(value=pdf_id))]
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
