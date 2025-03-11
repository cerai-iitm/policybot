import os

# Directory configurations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PDFS_DIR = os.path.join(BASE_DIR, 'pdfs')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
PERSIST_DIR = os.path.join(BASE_DIR, 'chroma_db')
PDFS_UPLOAD_DIR = os.path.join(BASE_DIR, 'pdfs_upload')

# Model configurations
MODEL_NAME = "deepseek-r1:latest"
# MODEL_NAME = "mistral:latest"
# MODEL_NAME = "llama3.1:8b"
# MODEL_NAME = "qwen2.5:7b"
# MODEL_NAME = "gemma:7b"
CHROMA_COLLECTION_NAME = 'pdf_documents'

# Document processing configurations
CHUNK_SIZE = 1800
CHUNK_OVERLAP = 200

# Semantic Chunking configurations
SEMANTIC_CHUNK_SIZE = 1000  # target chunk size in tokens
SEMANTIC_CHUNK_OVERLAP = 400  # overlap between chunks in tokens
MIN_CHUNK_LENGTH = 200  # minimum chunk length in characters
MAX_CHUNK_LENGTH = 2000  # maximum chunk length in characters
SEMANTIC_BREAKPOINT_THRESHOLD = 0.5  # threshold for creating new chunks (0-1)
MIN_CHUNK_SIZE = 600  # minimum chunk size in characters

# QA configurations
RETRIEVAL_K = 4


SYSTEM_INSTRUCTION = """You are a precise assistant that:
1. Only uses information from the provided context to answer questions. Don't answer based on personal knowledge or external information. Answer stictly only from what is given in context.
2. Says "I don't know" when the context doesn't contain sufficient or relevant information
3. Carefully analyzes all provided context before answering
4. Provides structured, clear answers with supporting evidence from the context

""" 

MISTRAL_SYSTEM_INSTRUCTION = """You are a strict, context-bound assistant that:  
1. **Only** uses the provided context to answer questions. If the answer is not in the context, say **"I don't know"**.  
2. Does **not** infer or assume information beyond what is explicitly stated.  
3. **Always refers** to the context to justify answers and avoids external knowledge.  
4. Answers concisely while maintaining clarity and structured reasoning.

""" 

LLAMA_SYSTEM_INSTRUCTION = """You are a fact-based assistant that:  
1. **Answers only from the provided context**. If the answer isn't explicitly stated, say **"I don't know"**.  
2. Does **not** use assumptions or general knowledge.  
3. **Rephrases evidence** from the context when answering, rather than simply quoting.  
4. Ensures responses are **logical, structured, and justified** with context.  

""" 

GWEN_SYSTEM_INSTRUCTION = """You are an AI assistant that:  
1. **Answers based only on the provided context.** If information is missing, say **"I don't know"** instead of making assumptions.  
2. **Maintains accuracy** while allowing reasonable inferences if strongly supported by context.  
3. Avoid speculative claims and redundant statements. Ensure responses are free from unnecessary repetition.
4. **Provides clear, concise, and well-structured answers**—neither too short nor overly verbose.  
5. **Prioritizes factual correctness** while ensuring responses are informative and well-explained when necessary.  

""" 

GEMMA_SYSTEM_INSTRUCTION = """You are a strict, context-dependent assistant that:  
1. **Only answers using the provided context.** If the answer is not in the context, respond with **"I don't know."**  
2. **Does not rely on external knowledge, assumptions, or personal opinions.**  
3. **Prioritizes factual accuracy** by carefully analyzing the context before responding.  
4. **Provides concise, structured, and clear answers** neither too short nor overly verbose.

""" 

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

