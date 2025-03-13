import logging
from datetime import datetime
import os
from ..config.settings import LOGS_DIR
import json
import warnings
import sys

def setup_logger(mode):
    """Setup a logger for a specific chat mode"""
    logger = logging.getLogger(mode)
    if not logger.handlers:
        os.makedirs(LOGS_DIR, exist_ok=True)
        file_handler = logging.FileHandler(
            os.path.join(LOGS_DIR, f'{mode}_{datetime.now().strftime("%Y%m%d")}.log'),
            encoding='utf-8'  # Explicitly use UTF-8 encoding for log files
        )
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
        # Prevent propagation to root logger (this stops console output)
        logger.propagate = False
    return logger

def log_rag_interaction(logger, question, context_docs, answer):
    """Log RAG-based interactions (regular chat and single PDF)"""
    try:
        contexts_with_sources = []
        for doc in context_docs:
            contexts_with_sources.append(
                f"\nSource: {doc.metadata.get('source', 'Unknown')}"
                f"\nContext: [Chunk {doc.metadata.get('chunk_number')}], Similarity: {doc.metadata.get('similarity', 'Unknown')} : {doc.page_content}"
            )
        log_entry = (
            f"\nQuestion: {question}\n"
            f"Sources and Contexts Used: {''.join(contexts_with_sources)}\n"
            f"Answer: {answer}\n"
            f"{'-'*80}"
        )
        logger.info(log_entry)
    except Exception as e:
        logger.error(f"Error in log_rag_interaction: {str(e)}")

def log_direct_interaction(logger, question, context, response_data):
    """Log direct chat interactions with reasoning steps"""
    try:
        log_entry = (
            f"\nQuestion: {question}\n"
            f"Provided Context: {context if context else 'None'}\n"
            f"{'-'*80}"
        )
        logger.info(log_entry)
    except Exception as e:
        logger.error(f"Error in log_direct_interaction: {str(e)}")

def configure_root_logger(console_level=logging.WARNING):
    """Configure the root logger to control console output"""
    # Suppress specific torch warning
    warnings.filterwarnings('ignore', message='.*Examining the path of torch.classes raised.*')
    
    # Filter out progress bar output
    logging.getLogger('tqdm').setLevel(logging.WARNING)
    
    root_logger = logging.getLogger()
    
    # Set the root logger level
    root_logger.setLevel(logging.INFO)
    
    # Remove any existing handlers to avoid duplication
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add a console handler with the specified level
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(console_level)
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add a filter to prevent Unicode errors in console output
    class UnicodeFilter(logging.Filter):
        def filter(self, record):
            if isinstance(record.msg, str):
                try:
                    # Test if message can be encoded with console encoding
                    record.msg.encode(sys.stdout.encoding or 'cp1252')
                except UnicodeEncodeError:
                    # Replace with a simplified message if encoding fails
                    record.msg = f"[Unicode message removed - see log file]"
            return True
    
    console_handler.addFilter(UnicodeFilter())
    root_logger.addHandler(console_handler)
    
    return root_logger