import os

# Directory configurations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PDFS_DIR = os.path.join(BASE_DIR, 'pdfs')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
PERSIST_DIR = os.path.join(BASE_DIR, 'chroma_db')

# Model configurations
MODEL_NAME = "deepseek-r1:1.5b"
CHROMA_COLLECTION_NAME = 'pdf_documents'

# Document processing configurations
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# QA configurations
RETRIEVAL_K = 5

# Prompt template
QA_TEMPLATE = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""
