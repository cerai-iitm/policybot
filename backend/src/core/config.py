import os

from dotenv import load_dotenv

from . import prompts

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
    # default model used by the backend for final generation
    MODEL_NAME: str = "unsloth/gemma-3n-E4B-it"
    TEMPERATURE = 0.1
    MAX_CONTEXT_TOKENS = 32000

    RERANKING_MODEL_NAME = "BAAI/bge-reranker-base"
    TOP_K = 10
    TOP_P = 0.9
    RERANKER_TEMP = 1.0
    RRF_TEMP = 0.17

    # TEI Reranker Configuration
    TEI_RERANKER_IP = os.getenv("TEI_RERANKER_IP", "localhost")
    TEI_RERANKER_PORT = int(os.getenv("TEI_RERANKER_PORT", "8080"))
    TEI_RERANKER_URL = f"http://{TEI_RERANKER_IP}:{TEI_RERANKER_PORT}"

    # vLLM Embedding Configuration (for retrieval queries)
    VLLM_EMBEDDING_ENABLED = (
        os.getenv("VLLM_EMBEDDING_ENABLED", "false").lower() == "true"
    )
    VLLM_EMBEDDING_IP = os.getenv("VLLM_EMBEDDING_IP", "localhost")
    VLLM_EMBEDDING_PORT = int(os.getenv("VLLM_EMBEDDING_PORT", "8081"))
    VLLM_EMBEDDING_URL = f"http://{VLLM_EMBEDDING_IP}:{VLLM_EMBEDDING_PORT}/v1"
    VLLM_EMBEDDING_MODEL = os.getenv(
        "VLLM_EMBEDDING_MODEL", "google/embeddinggemma-300m"
    )
    VLLM_EMBEDDING_API_KEY = os.getenv("VLLM_EMBEDDING_API_KEY", "EMPTY")

    # vLLM LLM Configuration (port 8080 - different from embeddings)
    VLLM_LLM_IP = os.getenv("VLLM_LLM_IP", "localhost")
    VLLM_LLM_PORT = int(os.getenv("VLLM_LLM_PORT", "8080"))
    VLLM_LLM_URL = f"http://{VLLM_LLM_IP}:{VLLM_LLM_PORT}/v1"
    VLLM_LLM_MODEL = os.getenv("VLLM_LLM_MODEL", "unsloth/gemma-3n-E4B-it")
    VLLM_LLM_API_KEY = os.getenv("VLLM_LLM_API_KEY", "EMPTY")
    VLLM_LLM_TEMPERATURE = float(os.getenv("VLLM_LLM_TEMPERATURE", "0.7"))
    VLLM_LLM_MAX_TOKENS = int(os.getenv("VLLM_LLM_MAX_TOKENS", "4096"))

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
        OLLAMA_URL = "http://localhost:11434"

    TEMP_FILE_PATH = "/tmp/policybot_temp.txt"

    # Prompt strings imported from src.prompts — keep all prompt content in one place.
    QUERY_REWRITE_SYSTEM_PROMPT = prompts.QUERY_REWRITE_SYSTEM_PROMPT
    SYSTEM_PROMPT = prompts.SYSTEM_PROMPT
    GENERATED_EXAMPLE_DOCUMENT_PROMPT = prompts.GENERATED_EXAMPLE_DOCUMENT_PROMPT
    APPLICATION_INSTRUCTIONS = prompts.APPLICATION_INSTRUCTIONS
    SUGGESTED_QUERIES_PROMPT = prompts.SUGGESTED_QUERIES_PROMPT

    # Admin config for testing models
    SUPPORTED_MODELS = [
        {"id": "gemma3n:e4b", "name": "Gemma 3n (e4b)"},
        {"id": "unsloth/gemma-3n-E4B-it", "name": "Gemma 3n E4B IT (unsloth)"},
        {
            "id": "hf.co/mradermacher/MiniMax-M2-THRIFT-55-i1-GGUF:Q3_K_S",
            "name": "MiniMax M2 Thrift 55",
        },
        {
            "id": "hf.co/mradermacher/MiniMax-M2-THRIFT-i1-GGUF:IQ2_XXS",
            "name": "MiniMax M2 Thrift XXS",
        },
        {"id": "llama4:latest", "name": "Llama 4 Latest"},
        {"id": "gemma3:27b-it-qat", "name": "Gemma 3 27B IT"},
    ]


cfg = Config()

if __name__ == "__main__":
    pass
