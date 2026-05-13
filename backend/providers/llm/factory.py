# providers/llm/factory.py
import httpx

from app.config import get_config
from app.logger import get_logger

config = get_config()
logger = get_logger(__name__)


def get_llm():
    """Factory function to get LLM based on config."""
    provider = config.llm_provider.lower()

    # Determine if using proxy
    use_proxy = config.dev_proxy_api_key is not None and config.dev_proxy_api_key != ""
    proxy_headers = {"X-API-Key": config.dev_proxy_api_key} if use_proxy else None

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        # Use proxy URL if set, otherwise direct URL
        url = config.ollama_proxy_url if use_proxy else config.ollama_url

        # Build client_kwargs with headers if using proxy
        client_kwargs = {"headers": proxy_headers} if use_proxy else None

        logger.info(
            f"Using Ollama LLM with {'proxy' if use_proxy else 'direct'} connection at {url}"
        )
        return ChatOllama(
            model=config.default_model,
            base_url=url,
            client_kwargs=client_kwargs,
            num_predict=config.num_predict,
            num_ctx=config.num_ctx,
            temperature=config.temperature,
        )

    elif provider == "gemini":
        if not config.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not set in .env")
        from langchain_google_genai import ChatGoogleGenerativeAI

        logger.info("Using Google Gemini LLM with direct connection")
        return ChatGoogleGenerativeAI(
            model=config.default_model,
            google_api_key=config.gemini_api_key,
        )

    elif provider in ("vllm", "openai"):
        from langchain_openai import ChatOpenAI

        # Use proxy URL if set, otherwise direct URL
        url = config.vllm_llm_proxy_url if use_proxy else config.vllm_llm_url

        # Determine API key: direct key > proxy key > "EMPTY" for vLLM
        if use_proxy:
            api_key = config.vllm_llm_api_key or config.dev_proxy_api_key or "EMPTY"
        else:
            api_key = config.vllm_llm_api_key or "EMPTY"

        # Build HTTP client with proxy headers if needed
        http_client = httpx.Client(headers=proxy_headers) if use_proxy else None

        logger.info(
            f"Using {'vLLM' if provider == 'vllm' else 'OpenAI'} LLM with {'proxy' if use_proxy else 'direct'} connection at {url}"
        )
        return ChatOpenAI(
            model=config.default_model,
            base_url=url,
            api_key=api_key,
            http_client=http_client,
        )

    raise ValueError(f"Unknown LLM provider: {provider}")
