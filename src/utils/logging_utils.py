import logging
from datetime import datetime
import os
from ..config.settings import LOGS_DIR
import json
import warnings

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
        # Prevent propagation to root logger (this stops console output)
        logger.propagate = False
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

def log_direct_interaction(logger, question, context, response_data):
    """Log direct chat interactions with reasoning steps"""
    # Handle both string responses and dictionary responses
    if isinstance(response_data, str):
        answer = response_data
        reasoning = "No structured reasoning provided"
        full_response = response_data
    else:
        answer = response_data.get("answer", "")
        reasoning = response_data.get("reasoning", "No structured reasoning provided")
        full_response = response_data.get("full_response", "")
    log_entry = (
        f"\nQuestion: {question}\n"
        f"Provided Context: {context if context else 'None'}\n"
        f"Reasoning Steps:\n{reasoning}\n"
        f"Answer: {answer}\n"
        f"Full Response: {full_response}\n"
        f"{'-'*80}"
    )
    logger.info(log_entry)

def log_evaluation(logger, question, context, llm_answer, human_answer, results):
    """Log evaluation of LLM answers against human reference answers"""
    metrics_details = "\n".join([
        f"Similarity: {results.get('similarity', 0):.3f}",
        f"ROUGE-1: {results.get('rouge1', 0):.3f}",
        f"ROUGE-2: {results.get('rouge2', 0):.3f}",
        f"ROUGE-L: {results.get('rougeL', 0):.3f}",
        f"Question Relevance: {results.get('question_relevance', 0):.3f}",
        f"Context Relevance: {results.get('context_relevance', 0):.3f}",
        f"Final Score: {results.get('final_score', 0):.3f}"
    ])
    
    log_entry = (
        f"\nQuestion: {question}\n"
        f"Context: {context[:200]}{'...' if len(context) > 200 else ''}\n"
        f"LLM Answer: {llm_answer}\n"
        f"Human Answer: {human_answer}\n"
        f"Evaluation Metrics:\n{metrics_details}\n"
        f"{'-'*80}"
    )
    logger.info(log_entry)

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
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    return root_logger