import os
import subprocess
import tempfile
import time
import warnings
from gc import set_debug
from typing import Any, Dict, List

import chromadb
import torch
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import cfg
from src.logger import logger

warnings.filterwarnings("ignore")


def load_embedding_model(device=None):
    if device is None:
        # Priority: MPS (Apple Silicon) > CUDA (NVIDIA) > CPU
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = "mps"
        elif torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"
    
    # For embedding models, use CPU for stability on macOS
    # MPS support for transformers can be inconsistent
    embedding_device = "cpu" if device == "mps" else device
    
    embedding_model = HuggingFaceEmbeddings(
        model_name=cfg.EMBEDDING_MODEL_NAME,
        model_kwargs={
            **cfg.EMBEDDING_MODEL_KWARGS,
            "device": embedding_device,
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
    elif device == "mps":
        # Clear MPS cache on Apple Silicon
        if hasattr(torch.backends.mps, 'empty_cache'):
            torch.backends.mps.empty_cache()


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
        for _, chunk in enumerate(chunks):
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


def run_retriever(query: str, file_name: str, top_k: int):
    import os
    import subprocess
    import tempfile

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".txt", delete=False, encoding="utf-8"
    ) as temp_file:
        temp_file_path = temp_file.name

    env = os.environ.copy()
    env["PYTHONPATH"] = project_root

    process = subprocess.Popen(
        [
            "python",
            "src/rag/retriever.py",
            query,
            file_name,
            str(top_k),
            temp_file_path,
        ],
        cwd=project_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    try:
        if process.stdout is not None:
            for line in iter(process.stdout.readline, ""):
                if line:
                    yield {"progress": line.strip()}
            process.stdout.close()
        process.wait()
    finally:
        try:
            os.unlink(temp_file_path)
        except OSError:
            pass

    if process.returncode != 0:
        yield {
            "success": False,
            "error": f"Retriever failed with exit code {process.returncode}",
        }
        return

    if not os.path.exists(temp_file_path) or os.path.getsize(temp_file_path) == 0:
        yield {"success": False, "error": "No output from retriever"}
        return

    with open(temp_file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    yield {"success": True, "chunks": content}


def process_pdf(file_name: str):
    import os
    import subprocess
    import tempfile

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".txt", delete=False, encoding="utf-8"
    ) as temp_file:
        temp_file_path = temp_file.name

    env = os.environ.copy()
    env["PYTHONPATH"] = project_root

    logger.info(f"Starting PDF processor subprocess for file: {file_name}")
    process = subprocess.Popen(
        ["python", "src/rag/pdf_processor.py", file_name, temp_file_path],
        cwd=project_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    try:
        if process.stdout is not None:
            for line in iter(process.stdout.readline, ""):
                if line:
                    yield {"progress": line.strip()}
            process.stdout.close()
        process.wait()
    finally:
        try:
            os.unlink(temp_file_path)
        except OSError:
            pass

    if process.returncode != 0:
        yield {
            "success": False,
            "error": f"PDF processor failed with exit code {process.returncode}",
        }
        return

    if not os.path.exists(temp_file_path) or os.path.getsize(temp_file_path) == 0:
        yield {"success": False, "error": "No output from PDF processor"}
        return

    with open(temp_file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    response = parse_response_from_text(content)
    yield response


def run_pdf_processor(file_name: str):
    import os
    import subprocess

    temp_file_path = cfg.TEMP_FILE_PATH
    # Optionally clear the file before use
    open(temp_file_path, "w").close()

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root

    process = subprocess.Popen(
        ["python", "src/rag/pdf_processor.py", file_name, temp_file_path],
        cwd=project_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    try:
        if process.stdout is not None:
            for line in iter(process.stdout.readline, ""):
                if line:
                    yield {"progress": line.strip()}
            process.stdout.close()
        process.wait()
    finally:
        pass  # Do not delete the temp file here

    yield {"temp_file_path": temp_file_path, "returncode": process.returncode}


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


def read_pdf_processor_result(temp_file_path: str):
    import os

    if not os.path.exists(temp_file_path) or os.path.getsize(temp_file_path) == 0:
        return {"success": False, "error": "No output from PDF processor"}

    with open(temp_file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    try:
        os.unlink(temp_file_path)
    except OSError:
        pass

    response = parse_response_from_text(content)
    return response


def run_retriever_subprocess(query: str, file_name: str, top_k: int):
    import os
    import subprocess
    import tempfile

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".txt", delete=False, encoding="utf-8"
    ) as temp_file:
        temp_file_path = temp_file.name

    env = os.environ.copy()
    env["PYTHONPATH"] = project_root

    process = subprocess.Popen(
        [
            "python",
            "src/rag/retriever.py",
            file_name,
            query,
            str(top_k),
            temp_file_path,
        ],
        cwd=project_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    try:
        if process.stdout is not None:
            for line in iter(process.stdout.readline, ""):
                if line:
                    yield {"progress": line.strip()}
            process.stdout.close()
        process.wait()
    finally:
        pass

    yield {"temp_file_path": temp_file_path, "returncode": process.returncode}


def read_retriever_result(temp_file_path: str):
    import os

    if not os.path.exists(temp_file_path) or os.path.getsize(temp_file_path) == 0:
        return {"success": False, "error": "No output from retriever"}

    with open(temp_file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    try:
        os.unlink(temp_file_path)
    except OSError:
        pass

    chunks = parse_chunks_from_text(content)
    if not chunks:
        return {
            "success": False,
            "error": "No relevant information found in the document for your query.",
        }
    return {"success": True, "chunks": chunks}


if __name__ == "__main__":
    pass
