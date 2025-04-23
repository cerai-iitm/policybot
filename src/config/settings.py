import os
from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    PDFS_DIR: str = os.path.join(BASE_DIR, 'pdfs')
    UPLOADS_DIR: str = os.path.join(BASE_DIR, 'uploads')
    VECTOR_STORE_DIR: str = os.path.join(BASE_DIR, 'vector_store')
    
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    
    GEMINI_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

    GEMINI_MODEL_NAME: str = "gemini-1.5-pro"
    EMBEDDING_MODEL_NAME: str = "models/embedding-001"
    
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    TOP_K_RESULTS: int = 4
    SIMILARITY_THRESHOLD: float = 0.7  
    
    SYSTEM_PROMPT: str = """You are an AI assistant specialized in analyzing AI policy documents. 
    Your task is to provide accurate, informative answers based ONLY on the context provided.
    
    Guidelines:
    1. Read and analyze the context carefully before answering
    2. Answer ONLY based on information in the context
    3. If the context doesn't contain the answer, say "I don't have enough information to answer this question"
    4. Be concise but thorough in your explanations
    5. When appropriate, cite specific policy sections by name/number
    6. Do not make up information or use prior knowledge outside the provided context
    7. Always maintain a balanced, objective tone
    """
    
    QA_PROMPT_TEMPLATE: str = """
    {system_prompt}
    
    Context information:
    {context}
    
    Question: {question}
    
    Answer:
    """

settings = Settings()

