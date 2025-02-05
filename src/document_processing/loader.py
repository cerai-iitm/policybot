import os
import logging
from typing import List
from langchain_community.document_loaders import PyPDFLoader, PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from ..config.settings import CHUNK_SIZE, CHUNK_OVERLAP, PDFS_UPLOAD_DIR

logger = logging.getLogger(__name__)

def upload_pdf(file):
    file_path = os.path.join(PDFS_UPLOAD_DIR, file.name)
    with open(file_path, "wb") as f:
        f.write(file.getvalue())
    return file_path

def is_valid_pdf(file_path: str) -> bool:
    try:
        # Try to open and read the PDF with pypdf
        with open(file_path, 'rb') as file:
            PdfReader(file)
        return True
    except Exception as e:
        logger.error(f"Invalid PDF file {file_path}: {str(e)}")
        return False

def load_pdf(file_path: str) -> List:
    """Load a PDF file and return its content as documents."""
    try:
        if not is_valid_pdf(file_path):
            logger.warning(f"Skipping invalid PDF: {file_path}")
            return []
        
        # Try PyPDFLoader first, fall back to PDFPlumberLoader if it fails
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
        except Exception:
            loader = PDFPlumberLoader(file_path)
            documents = loader.load()
        
        logger.info(f"Successfully loaded PDF: {file_path}")
        return documents
    except Exception as e:
        logger.error(f"Error loading PDF {file_path}: {str(e)}")
        return []

def split_text(documents: List) -> List:
    """Split documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True
    )
    return text_splitter.split_documents(documents)
