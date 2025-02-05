import os

# Directory configurations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PDFS_DIR = os.path.join(BASE_DIR, 'pdfs')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
PERSIST_DIR = os.path.join(BASE_DIR, 'chroma_db')
PDFS_UPLOAD_DIR = os.path.join(BASE_DIR, 'pdfs_upload')

# Model configurations
MODEL_NAME = "deepseek-r1:latest"
CHROMA_COLLECTION_NAME = 'pdf_documents'

# Document processing configurations
CHUNK_SIZE = 1400
CHUNK_OVERLAP = 200

# QA configurations
RETRIEVAL_K = 5

# New system instruction for the prompt.
SYSTEM_INSTRUCTION = "Only use the provided context to answer and not anything else. If you don't know the answer, say 'I don't know it.'"

# Prompt template
QA_TEMPLATE = """
{{- if .System }}{{ .System }}{{ end }}
You are an assistant for question-answering tasks.
Question: {question} 
Context: {context} 
Answer:
"""
