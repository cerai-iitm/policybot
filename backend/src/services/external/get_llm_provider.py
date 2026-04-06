from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from src.core import cfg, logger


def get_llm(
    provider: str | None = None,
    model_name: str | None = None,
) -> BaseChatModel:
    provider = (provider or cfg.LLM_PROVIDER).lower()

    if provider == "gemini":
        api_key = cfg.GEMINI_API_KEY
        if not api_key or not api_key.strip():
            raise ValueError("GEMINI_API_KEY is not set in config")

        return ChatGoogleGenerativeAI(
            model=model_name or "gemini-2.5-flash",
            google_api_key=api_key,
            temperature=cfg.TEMPERATURE,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

    if provider == "ollama":
        model = model_name or cfg.SUPPORTED_MODELS[0].get("id", "llama3")
        api_key = cfg.OLLAMA_PROXY_API_KEY or cfg.DEV_PROXY_API_KEY
        client_kwargs = {"headers": {"X-API-Key": api_key}} if api_key else None
        return ChatOllama(
            model=model,
            temperature=cfg.TEMPERATURE,
            base_url=cfg.OLLAMA_URL,
            num_ctx=cfg.MAX_CONTEXT_TOKENS,
            client_kwargs=client_kwargs,
        )

    if provider == "vllm":
        return ChatOpenAI(
            model=model_name or cfg.VLLM_LLM_MODEL,
            api_key=SecretStr(cfg.VLLM_LLM_API_KEY) or SecretStr("no-key"),
            base_url=cfg.VLLM_LLM_URL,
            temperature=cfg.VLLM_LLM_TEMPERATURE,
            max_tokens=cfg.VLLM_LLM_MAX_TOKENS,
        )

    raise ValueError(
        f"Unknown LLM_PROVIDER: '{provider}'. "
        f"Supported providers: 'gemini', 'ollama', 'vllm'"
    )


def extract_llm_output(response) -> str:
    if hasattr(response, "content"):
        return response.content
    elif isinstance(response, str):
        return response
    elif isinstance(response, dict) and "content" in response:
        return response["content"]
    else:
        logger.error(
            f"Unknown response format: {type(response)}. "
            f"Expected object with .content, string, or dict with 'content' key."
        )
        raise ValueError(
            f"Unknown response format from LLM: {type(response)}. "
            f"Cannot extract text content."
        )
