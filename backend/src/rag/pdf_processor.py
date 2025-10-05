import asyncio
import os
import sys
import warnings
from typing import AsyncGenerator, List

import chromadb
import numpy as np
import pymupdf
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
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

    async def process_pdf(self, file_name: str) -> AsyncGenerator[str, None]:
        self.chroma_client = await chromadb.AsyncHttpClient(host="localhost", port=8500)
        self.collection = await self.chroma_client.get_or_create_collection(
            name=cfg.COLLECTION_NAME
        )

        logger.info(f"Processing PDF file: {file_name}")
        yield "Starting PDF processing..."
        await asyncio.sleep(0)  # Force flush

        yield "Checking for existing embeddings..."
        await asyncio.sleep(0)
        if await self._check_existing_embeddings(file_name):
            yield "Embeddings already exist. Skipping processing."
            yield "done"
            return

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
        embeddings = await asyncio.to_thread(self._embed_docs, split_docs, file_name)
        if embeddings is None:
            yield "Error: Failed to generate embeddings."
            return
        logger.info(f"Generated embeddings shape: {embeddings.shape} for {file_name}.")

        yield "Saving embeddings to database..."
        await asyncio.sleep(0)
        await self._store_embeddings(split_docs, embeddings, file_name)
        logger.info(f"Successfully processed and stored embeddings for {file_name}.")

        yield "Creating summary..."
        await asyncio.sleep(0)
        summary_result = await asyncio.to_thread(self._create_summary, docs, file_name)
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

    def _create_summary(
        self, docs: List[Document], file_name: str
    ) -> tuple[str, str] | None:
        logger.info(f"Creating a summary for {file_name}.")
        try:
            existing_summary = get_summary_by_source_name(
                cfg.DB_SESSION, os.path.basename(file_name)
            )
            if existing_summary:
                logger.info(
                    f"Summary already exists for {file_name}. Skipping sumamary creation."
                )
                return file_name, existing_summary

            text = "\n".join([doc.page_content for doc in docs])
            doc = Document(page_content=text, metadata={"source": file_name})
            splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=0)
            recursive_docs = splitter.split_documents([doc])
            logger.info(
                f"Split text into {len(recursive_docs)} chunks for summarization."
            )

            chain = load_summarize_chain(self.interface.llm, chain_type="map_reduce")
            summary = chain.invoke({"input_documents": recursive_docs})
            add_source_summary(
                cfg.DB_SESSION,
                source_name=os.path.basename(file_name),
                summary=summary["output_text"],
            )
            return file_name, summary["output_text"]

        except Exception as e:
            logger.error(f"Error creating summary for {file_name}: {e}")
            return

    def _extract_text_from_pdf(self, file_name: str) -> list[Document] | None:
        file_path = os.path.join(cfg.DATA_DIR, file_name)
        logger.info(f"Extracting text from PDF file: {file_path}")

        if not os.path.exists(file_path):
            logger.error(f"PDF file not found: {file_path}")
            return None

        try:
            pdf_doc = pymupdf.open(file_path)
            documents = []

            for page_num, page in enumerate(pdf_doc):
                text = page.get_text("text").strip()

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
        existing_docs = await self.collection.get(where={"source": file_name}, limit=1)
        if existing_docs and existing_docs.get("ids"):
            logger.info(
                f"Document embeddings already exist in the database for {file_name}."
            )
            return True
        logger.info(f"No existing embeddings found in the database for {file_name}.")
        return False

    def _run_splitter(
        self, docs: List[Document], file_name: str
    ) -> List[Document] | None:
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

    def _embed_docs(self, docs: List[Document], file_name: str) -> np.ndarray | None:
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
        logger.info(f"Saving embeddings to db for {file_name}")
        try:
            ids = [f"{file_name}_{i}" for i in range(len(docs))]
            await self.collection.add(
                ids=ids,
                documents=[doc.page_content for doc in docs],
                embeddings=embeddings.tolist(),
                metadatas=[{"source": file_name} for _ in range(len(docs))],
            )
            logger.info(f"Stored embeddings for {len(docs)} chunks.")
        except Exception as e:
            logger.error(f"Error storing embeddings: {e}")


if __name__ == "__main__":

    def format_response_to_text(
        success: bool, message: str = "", error: str = ""
    ) -> str:
        try:
            if success:
                content = f"SUCCESS\n{message}"
            else:
                content = f"ERROR\n{error}"

            return f"{cfg.RESPONSE_START}{content}{cfg.RESPONSE_END}"

        except Exception as e:
            return f"{cfg.RESPONSE_START}ERROR\n{str(e)}{cfg.RESPONSE_END}"

    if len(sys.argv) != 3:
        result = format_response_to_text(
            False, error="Usage: python pdf_processor.py <file_name> <output_file>"
        )
        print(result)
        sys.exit(1)

    file_name = sys.argv[1]
    output_file = sys.argv[2]

    try:
        processor = PDFProcessor()
        success = processor.process_pdf(file_name)

        if success:
            result_text = format_response_to_text(
                True, f"PDF {file_name} processed successfully"
            )
        else:
            result_text = format_response_to_text(
                False, error=f"Failed to process PDF {file_name}"
            )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result_text)

    except Exception as e:
        error_result = format_response_to_text(False, error=str(e))
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(error_result)
        except:
            print(error_result)
