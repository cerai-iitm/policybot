import os

from dotenv import load_dotenv

# Import prompt constants from prompts module (moved out of this file)
from src import prompts

load_dotenv()


class Config:
    ALLOWED_EXTENSIONS = ["pdf"]

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")

    # Do not create a global synchronous DB session in async app.
    # Routes and services should use the async dependency `get_db` from src.schema.db.
    DB_SESSION = None

    COLLECTION_NAME = "pdf_embeddings"

    IN_DOCKER = os.getenv("IN_DOCKER", "0") == "1"
    QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant" if IN_DOCKER else "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

    # Database config
    DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
    DB_USER = os.getenv("POSTGRES_USER", "postgres")
    DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
    DB_NAME = os.getenv("POSTGRES_DB", "policybot")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")
    DATABASE_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    EMBEDDING_MODEL_NAME = "Alibaba-NLP/gte-multilingual-base"
    EMBEDDING_MODEL_KWARGS = {"trust_remote_code": True}
    ENCODE_KWARGS = {"normalize_embeddings": True}
    BREAKPOINT_THRESHOLD_TYPE = "standard_deviation"
    BREAKPOINT_THRESHOLD_AMOUNT = 1.0
    MAX_HISTORY_MESSAGES = 3
    MODEL_NAME = "gemma3n:e4b"
    TEMPERATURE = 0.1
    MAX_CONTEXT_TOKENS = 32000

    RERANKING_MODEL_NAME = "BAAI/bge-reranker-base"
    TOP_K = 10
    TOP_P = 0.9
    RERANKER_TEMP = 1.3
    RRF_TEMP = 0.17

    CHUNK_SEPARATOR = "###$$$%%%^^^&&&***"
    CHUNK_PREFIX = "CHUNK_"
    RESPONSE_START = "RESPONSE_START" + CHUNK_SEPARATOR
    RESPONSE_END = CHUNK_SEPARATOR + "RESPONSE_END"
    OVERALL_SUMMARY_MAX_WORDS = 400

    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")

    FRONTEND_URL = "http://localhost:3000"
    OLLAMA_PORT = os.environ.get("OLLAMA_PORT", "11434")
    OLLAMA_IP = os.environ.get("OLLAMA_IP", "host.docker.internal")

    if os.environ.get("IN_DOCKER") == "1":
        OLLAMA_URL = f"http://{OLLAMA_IP}:{OLLAMA_PORT}"
    else:
        OLLAMA_URL = f"http://localhost:11434"

    TEMP_FILE_PATH = "/tmp/policybot_temp.txt"

    # Prompt strings imported from src.prompts — keep all prompt content in one place.
    QUERY_REWRITE_SYSTEM_PROMPT = prompts.QUERY_REWRITE_SYSTEM_PROMPT
    SYSTEM_PROMPT = prompts.SYSTEM_PROMPT
    GENERATED_EXAMPLE_DOCUMENT_PROMPT = prompts.GENERATED_EXAMPLE_DOCUMENT_PROMPT
    APPLICATION_INSTRUCTIONS = prompts.APPLICATION_INSTRUCTIONS
    SUGGESTED_QUERIES_PROMPT = prompts.SUGGESTED_QUERIES_PROMPT


cfg = Config()

if __name__ == "__main__":
    pass
