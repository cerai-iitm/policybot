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
CHUNK_SIZE = 1800
CHUNK_OVERLAP = 200

# Semantic Chunking configurations
SEMANTIC_CHUNK_SIZE = 400  # target chunk size in tokens
SEMANTIC_CHUNK_OVERLAP = 100  # overlap between chunks in tokens
MIN_CHUNK_LENGTH = 200  # minimum chunk length in characters
MAX_CHUNK_LENGTH = 2000  # maximum chunk length in characters
SEMANTIC_BREAKPOINT_THRESHOLD = 0.5  # threshold for creating new chunks (0-1)
MIN_CHUNK_SIZE = 200  # minimum chunk size in characters

# QA configurations
RETRIEVAL_K = 5

SYSTEM_INSTRUCTION = """You are a precise assistant that:
1. Only uses information from the provided context to answer questions. Don't answer based on personal knowledge or external information. Answer stictly only from what is given in context.
2. Says "I don't know" when the context doesn't contain sufficient or relevant information
3. Carefully analyzes all provided context before answering
4. Provides structured, clear answers with supporting evidence from the context"""

# Enhanced QA template for better context utilization
QA_TEMPLATE = """
{{- if .System }}{{ .System }}{{ end }}

Instructions for context analysis:
1. First, scan all provided context carefully
2. Identify relevant information that directly answers the question
3. If the context doesn't contain sufficient relevant information, say "I don't know"
4. Use specific examples and details from the context when available

Question: {question}
Context: {context}
Answer (provide a well-structured response using specific details from the context):"""

# Document handling templates
# DOCUMENT_PROMPT = """
# Context:
# content: {page_content}
# source: {source}
# """

# QA_CHAIN_PROMPT = """
# {system_instruction}
# Use the following pieces of context to provide an accurate answer to the question. 
# If you don't know the answer, just say that you don't know.

# {context}

# Question: {question}
# Answer:"""

# Prompt template
# QA_TEMPLATE = """
# {{- if .System }}{{ .System }}{{ end }}
# You are an assistant for question-answering tasks.
# Question: {question} 
# Context: {context} 
# Answer:
# """
