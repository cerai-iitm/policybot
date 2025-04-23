import os
import logging
from datetime import datetime
import json
from pathlib import Path
from typing import List, Dict, Any
from langchain_core.documents import Document

from ..config.settings import settings

LOGS_DIR = os.path.join(settings.BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

def setup_rag_logger():
    logger = logging.getLogger("rag_logger")
    
    if not logger.handlers:
        log_file = os.path.join(LOGS_DIR, f'rag_interactions_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')

        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)

        logger.propagate = False
    
    return logger

def log_interaction(question: str, documents: List[Document], answer: str):
    logger = setup_rag_logger()
    
    try:
        context_details = []
        full_chunk_texts = []
        
        for i, doc in enumerate(documents):
            source = doc.metadata.get("source", "Unknown Source")
            page = doc.metadata.get("page", "Unknown Page")
            chunk_index = doc.metadata.get("chunk_index", i)
            
            doc_details = {
                "chunk_number": i + 1,
                "source": source,
                "page": page,
                "chunk_index": chunk_index,
                "chunk_size": len(doc.page_content),
            }
            context_details.append(doc_details)
            
            chunk_header = f"\n\n{'='*40}\nCHUNK #{i+1}: [Source: {source}, Page: {page}, Index: {chunk_index}]\n{'='*40}\n"
            chunk_content = f"{doc.page_content}\n"
            full_chunk_texts.append(chunk_header + chunk_content)
        
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": question,
            "answer": answer,
            "retrieved_chunks": {
                "count": len(documents),
                "details": context_details
            }
        }
        
        formatted_log = json.dumps(log_entry, indent=2, ensure_ascii=False)
        
        logger.info(f"\n{'#'*100}\nQUESTION: {question}\n{'#'*100}")
        logger.info(formatted_log)
        
        if full_chunk_texts:
            logger.info(f"\nRETRIEVED CHUNKS (Full Content):\n{''.join(full_chunk_texts)}")
        else:
            logger.info("\nNo chunks were retrieved for this question.")
            
        logger.info(f"\n{'#'*100}\nANSWER:\n{answer}\n{'#'*100}\n\n")
        
    except Exception as e:
        logger.error(f"Error logging RAG interaction: {str(e)}")