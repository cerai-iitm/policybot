import os
import subprocess
import tempfile
import time
from typing import Any, Dict, List

import chromadb
import streamlit as st
import torch
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import cfg
from src.logger import logger


def load_embedding_model(device=None):
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    embedding_model = HuggingFaceEmbeddings(
        model_name=cfg.EMBEDDING_MODEL_NAME,
        model_kwargs={
            **cfg.EMBEDDING_MODEL_KWARGS,
            "device": device,
        },
        encode_kwargs=cfg.ENCODE_KWARGS,
    )
    return embedding_model, device


def free_embedding_model(embedding_model, device):
    del embedding_model
    import gc

    gc.collect()
    if device == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.synchronize()


def parse_chunks_from_text(content: str) -> List[str]:
    try:

        if cfg.RESPONSE_START not in content or cfg.RESPONSE_END not in content:
            logger.error("Invalid response format - missing markers")
            return []

        start_idx = content.find(cfg.RESPONSE_START) + len(cfg.RESPONSE_START)
        end_idx = content.find(cfg.RESPONSE_END)
        response_content = content[start_idx:end_idx].strip()

        if not response_content:
            return []

        chunk_parts = response_content.split(cfg.CHUNK_SEPARATOR)
        chunks = []

        for part in chunk_parts:
            part = part.strip()
            if part.startswith(cfg.CHUNK_PREFIX):

                chunk_content = part[len(cfg.CHUNK_PREFIX) :].strip()
                if chunk_content:
                    chunks.append(chunk_content)

        return chunks

    except Exception as e:
        logger.error(f"Error parsing chunks from text: {e}")
        return []


def format_chunks_to_text(chunks: List[str]) -> str:
    try:
        formatted_chunks = []
        for i, chunk in enumerate(chunks):
            formatted_chunks.append(f"{cfg.CHUNK_PREFIX}{chunk}")

        content = cfg.CHUNK_SEPARATOR.join(formatted_chunks)
        return f"{cfg.RESPONSE_START}{content}{cfg.RESPONSE_END}"

    except Exception as e:
        logger.error(f"Error formatting chunks to text: {e}")
        return ""


def parse_response_from_text(content: str) -> Dict[str, Any]:
    try:

        if cfg.RESPONSE_START not in content or cfg.RESPONSE_END not in content:
            logger.error("Invalid response format - missing markers")
            return {"success": False, "error": "Invalid response format"}

        start_idx = content.find(cfg.RESPONSE_START) + len(cfg.RESPONSE_START)
        end_idx = content.find(cfg.RESPONSE_END)
        response_content = content[start_idx:end_idx].strip()

        lines = response_content.split("\n")
        if not lines:
            return {"success": False, "error": "Empty response"}

        status_line = lines[0].strip()
        message = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

        if status_line.startswith("SUCCESS"):
            return {"success": True, "message": message}
        elif status_line.startswith("ERROR"):
            return {"success": False, "error": message}
        else:
            return {"success": False, "error": f"Unknown status: {status_line}"}

    except Exception as e:
        logger.error(f"Error parsing response from text: {e}")
        return {"success": False, "error": str(e)}


def format_response_to_text(success: bool, message: str = "", error: str = "") -> str:
    try:
        if success:
            content = f"SUCCESS\n{message}"
        else:
            content = f"ERROR\n{error}"

        return f"{cfg.RESPONSE_START}{content}{cfg.RESPONSE_END}"

    except Exception as e:
        logger.error(f"Error formatting response to text: {e}")
        return f"{cfg.RESPONSE_START}ERROR\n{str(e)}{cfg.RESPONSE_END}"


def run_retriever(query: str, file_name: str, top_k: int = cfg.TOP_K) -> List[str]:
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

        with tempfile.NamedTemporaryFile(
            mode="w+", suffix=".txt", delete=False, encoding="utf-8"
        ) as temp_file:
            temp_file_path = temp_file.name

        env = os.environ.copy()
        env["PYTHONPATH"] = project_root

        logger.info(f"Starting retriever subprocess for file: {file_name}")
        result = subprocess.run(
            [
                "python",
                "src/rag/retriever.py",
                file_name,
                query,
                str(top_k),
                temp_file_path,
            ],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_root,
            env=env,
        )

        max_wait_time = 30
        wait_time = 0
        while (
            not os.path.exists(temp_file_path) or os.path.getsize(temp_file_path) == 0
        ):
            time.sleep(0.1)
            wait_time += 0.1
            if wait_time > max_wait_time:
                logger.error("Timeout waiting for retriever output file")
                return []

        try:
            with open(temp_file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if not content:
                logger.warning("Retriever returned empty output")
                return []

            chunks = parse_chunks_from_text(content)
            return chunks

        finally:
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass

    except subprocess.CalledProcessError as e:
        st.error(f"Retriever script failed: {e.stderr}")
        logger.error(f"Retriever script error: {e}")
        return []
    except Exception as e:
        st.error(f"An error occurred while running the retriever: {e}")
        logger.error(f"Error running retriever: {e}")
        return []


def process_pdf(file_name: str) -> Dict[str, Any]:
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

        with tempfile.NamedTemporaryFile(
            mode="w+", suffix=".txt", delete=False, encoding="utf-8"
        ) as temp_file:
            temp_file_path = temp_file.name

        env = os.environ.copy()
        env["PYTHONPATH"] = project_root

        logger.info(f"Starting PDF processor subprocess for file: {file_name}")
        result = subprocess.run(
            ["python", "src/rag/pdf_processor.py", file_name, temp_file_path],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_root,
            env=env,
        )

        max_wait_time = 300
        wait_time = 0
        while (
            not os.path.exists(temp_file_path) or os.path.getsize(temp_file_path) == 0
        ):
            time.sleep(0.5)
            wait_time += 0.5
            if wait_time > max_wait_time:
                logger.error("Timeout waiting for PDF processor output file")
                return {"success": False, "error": "Timeout waiting for PDF processor"}

        try:
            with open(temp_file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if not content:
                logger.warning("PDF processor returned empty output")
                return {"success": False, "error": "Empty response from PDF processor"}

            response = parse_response_from_text(content)
            logger.info(f"PDF processing completed")
            return response

        finally:
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass

    except subprocess.CalledProcessError as e:
        error_msg = (
            f"PDF processor script failed with exit code {e.returncode}: {e.stderr}"
        )
        st.error(error_msg)
        logger.error(f"PDF processor error: {e}")
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"An error occurred while running the PDF processor: {e}"
        st.error(error_msg)
        logger.error(f"Error running PDF processor: {e}")
        return {"success": False, "error": error_msg}


def get_pdf_files_with_embeddings():
    os.makedirs(cfg.DATA_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=cfg.CHROMA_DIR)
    collection = client.get_or_create_collection(name=cfg.COLLECTION_NAME)
    pdf_files = [f for f in os.listdir(cfg.DATA_DIR) if f.lower().endswith(".pdf")]
    valid_files = []
    for file in pdf_files:
        existing = collection.get(where={"source": file}, limit=1)
        if existing and existing.get("ids"):
            valid_files.append(file)
    return valid_files


def has_embeddings(file_name: str) -> bool:
    client = chromadb.PersistentClient(path=cfg.CHROMA_DIR)
    collection = client.get_or_create_collection(name=cfg.COLLECTION_NAME)
    existing = collection.get(where={"source": file_name}, limit=1)
    return bool(existing and existing.get("ids"))


def save_summary_to_sqlite(file_name: str, summary: str):
    import sqlite3

    os.makedirs(cfg.DB_DIR, exist_ok=True)
    db_path = os.path.join(cfg.DB_DIR, "summaries.db")
    conn = sqlite3.connect(db_path)
    try:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS summaries (
                file_name TEXT PRIMARY KEY,
                summary TEXT
            )
            """
        )
        c.execute(
            """
            INSERT OR REPLACE INTO summaries (file_name, summary)
            VALUES (?, ?)
            """,
            (file_name, summary),
        )
        logger.info(f"Summary saved for {file_name} in SQLite database.")
        conn.commit()
    finally:
        conn.close()


def get_summary_from_sqlite(file_name: str) -> str | None:
    import sqlite3

    db_path = os.path.join(cfg.DB_DIR, "summaries.db")
    if not os.path.exists(db_path):
        return None
    conn = sqlite3.connect(db_path)
    try:
        c = conn.cursor()
        c.execute("SELECT summary FROM summaries WHERE file_name = ?", (file_name,))
        row = c.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


if __name__ == "__main__":
    pass
