import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    PDFS_DIR: str = os.path.join(BASE_DIR, 'pdfs')
    UPLOADS_DIR: str = os.path.join(BASE_DIR, 'uploads')
    VECTOR_STORE_DIR: str = os.path.join(BASE_DIR, 'db')
    LOGS_DIR: str = os.path.join(BASE_DIR, 'logs')
    
    def create_directories(self):
        for directory in [self.PDFS_DIR, self.UPLOADS_DIR, self.VECTOR_STORE_DIR, self.LOGS_DIR]:
            os.makedirs(directory, exist_ok=True)
    
    GEMINI_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

    GEMINI_MODEL_NAME: str = "models/gemini-2.0-flash"
    EMBEDDING_MODEL_NAME: str = "models/text-embedding-004"
    
    # Optimized chunking parameters for policy documents
    CHUNK_SIZE: int = 1200  # Increased to capture more context in policy sections
    CHUNK_OVERLAP: int = 300  # Increased overlap to maintain context across chunks
    
    # Enhanced retrieval parameters
    TOP_K_RESULTS: int = 10  # Retrieve more candidates for reranking
    SIMILARITY_THRESHOLD: float = 0.45  # Slightly lowered to catch more potential matches before reranking
    
    # Policy-specific system prompt
    SYSTEM_PROMPT: str = """You are an AI assistant specialized in analyzing AI policy documents. 
    Your task is to provide accurate, informative answers based ONLY on the context provided.
    
    Guidelines:
    1. Read and analyze the context carefully before answering
    2. Answer ONLY based on information in the context
    3. If the context doesn't contain the answer, say "I don't have enough information to answer this question"
    4. Be concise but thorough in your explanations
    5. When appropriate, cite specific policy sections by name/number
    6. Use formal language appropriate for policy documentation
    7. When citing sections, refer to them as they appear in the document (e.g., "Section 3.2", "Article IV")
    8. Do not make up information or use prior knowledge outside the provided context
    9. Always maintain a balanced, objective tone
    """
    
    # Enhanced prompt template with improved instructions
    QA_PROMPT_TEMPLATE: str = """
    {system_prompt}
    
    Context:
    ---
    {context}
    ---
    
    Question: {question}
    
    """

settings = Settings()
settings.create_directories()

