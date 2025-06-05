import os
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..document_processing.pdf_processor import PDFProcessor
from ..vector_store.vector_store import VectorStoreManager
from ..qa_system.qa_system import QASystem
from ..config.settings import settings
from ..utils.log_utils import log_interaction

logger = logging.getLogger(__name__)

class SinglePDFApp:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.current_pdf_path = None
        self.current_pdf_name = None
    
    def process_pdf(self, file_path: str) -> bool:
        if not os.path.exists(file_path):
            logger.error(f"PDF file not found: {file_path}")
            return False
            
        try:
            self.current_pdf_path = file_path
            self.current_pdf_name = Path(file_path).name
            
            collection_name = f"pdf_{Path(file_path).stem}"
            
            logger.info(f"Processing PDF: {self.current_pdf_name}")
            chunks = self.pdf_processor.process_pdf(file_path)
            
            if not chunks:
                logger.error(f"Failed to extract content from {self.current_pdf_name}")
                return False
                
            vector_store = VectorStoreManager(collection_name=collection_name)
            
            vector_store.clear()
            success = vector_store.add_documents(chunks)
            
            if success:
                logger.info(f"Successfully indexed {len(chunks)} chunks from {self.current_pdf_name}")
            else:
                logger.error(f"Failed to index chunks from {self.current_pdf_name}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return False
    
    def save_and_process_uploaded_pdf(self, file_content: bytes, filename: str) -> bool:
        try:
            file_path = self.pdf_processor.save_upload(file_content, filename)
            
            if not file_path:
                return False
                
            return self.process_pdf(file_path)
            
        except Exception as e:
            logger.error(f"Error processing uploaded PDF: {str(e)}")
            return False
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        if not self.current_pdf_path:
            return {
                "answer": "Please upload a PDF document first.",
                "sources": []
            }
        try:
            collection_name = f"pdf_{Path(self.current_pdf_path).stem}"
            vector_store = VectorStoreManager(collection_name=collection_name)
            # Use hybrid_search for better retrieval
            retrieved_docs = vector_store.hybrid_search(question)
            if not retrieved_docs:
                response = {
                    "answer": "I couldn't find relevant information in the document to answer your question.",
                    "sources": [{"title": self.current_pdf_name, "page": "N/A"}]
                }
                log_interaction(question, [], response["answer"])
                return response
            qa_system = QASystem()
            result = qa_system.answer_question(question, retrieved_docs)
            log_interaction(question, retrieved_docs, result["answer"])
            return result
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return {
                "answer": "I encountered an error while trying to answer your question.",
                "sources": []
            }