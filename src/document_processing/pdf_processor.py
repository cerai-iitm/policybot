import os
import logging
from typing import List
from pathlib import Path
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from ..config.settings import settings

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
    def load_pdf(self, file_path: str) -> List[Document]:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return []
            
        try:
            documents = []
            pdf_filename = Path(file_path).name
            
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    if text.strip(): 
                        doc = Document(
                            page_content=text,
                            metadata={
                                "source": pdf_filename,
                                "page": i + 1,
                                "file_path": file_path
                            }
                        )
                        documents.append(doc)
            
            logger.info(f"Successfully extracted {len(documents)} pages from {pdf_filename}")
            return documents
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            return []
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        if not documents:
            return []
            
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=["\n\n", "\n", ". ", " ", ""],
                length_function=len
            )
          
            chunks = text_splitter.split_documents(documents)
            
            for i, chunk in enumerate(chunks):
                chunk.metadata["chunk_index"] = i
            
            logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking documents: {str(e)}")
            return documents 
            
    def process_pdf(self, file_path: str) -> List[Document]:
        documents = self.load_pdf(file_path)
        if not documents:
            return []
            
        chunks = self.chunk_documents(documents)
        return chunks
        
    def save_upload(self, file_content: bytes, filename: str) -> str:
        upload_path = os.path.join(settings.UPLOADS_DIR, filename)
        
        try:
            with open(upload_path, "wb") as f:
                f.write(file_content)
            logger.info(f"Saved uploaded file to {upload_path}")
            return upload_path
        except Exception as e:
            logger.error(f"Error saving uploaded file: {str(e)}")
            return ""