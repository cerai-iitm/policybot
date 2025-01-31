import logging
from datetime import datetime
import os
from ..config.settings import LOGS_DIR

def setup_logger(mode):
    """Setup a logger for a specific chat mode"""
    logger = logging.getLogger(mode)
    if not logger.handlers:
        os.makedirs(LOGS_DIR, exist_ok=True)
        file_handler = logging.FileHandler(
            os.path.join(LOGS_DIR, f'{mode}_{datetime.now().strftime("%Y%m%d")}.log')
        )
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
    return logger

def log_rag_interaction(logger, question, context_docs, answer):
    """Log RAG-based interactions (regular chat and single PDF)"""
    contexts_with_sources = []
    for doc in context_docs:
        contexts_with_sources.append(
            f"\nSource: {doc.metadata.get('source', 'Unknown')}"
            f"\nContext: {doc.page_content}"
        )
    
    log_entry = (
        f"\nQuestion: {question}\n"
        f"Sources and Contexts Used: {''.join(contexts_with_sources)}\n"
        f"Answer: {answer}\n"
        f"{'-'*80}"
    )
    logger.info(log_entry)

def log_direct_interaction(logger, question, context, answer):
    """Log direct chat interactions"""
    log_entry = (
        f"\nQuestion: {question}\n"
        f"Provided Context: {context if context else 'None'}\n"
        f"Answer: {answer}\n"
        f"{'-'*80}"
    )
    logger.info(log_entry)
