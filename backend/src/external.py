from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama.llms import OllamaLLM
from src.config import cfg
from src.logger import logger


class External:
    def __init__(self) -> None:
        self.llm_instance = None

    def get_llm(self):
        if self.llm_instance is None:
            self.llm_instance = self._initialize_llm()
            if self.llm_instance is None:
                raise ValueError(
                    "Failed to initialize LLM. Check LLM_PROVIDER configuration."
                )
        return self.llm_instance

    def _initialize_llm(self):
        provider = cfg.LLM_PROVIDER.lower()
        if provider == "gemini":
            api_key = cfg.GEMINI_API_KEY
            if not api_key:
                raise ValueError("GEMINI_API_KEY is not set in config.")
            gemini_llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=api_key,
                temperature=cfg.TEMPERATURE,
                max_tokens=None,
                timeout=None,
                max_retries=2,
            )
            return gemini_llm

        elif provider == "ollama":
            return OllamaLLM(
                model=cfg.MODEL_NAME,
                temperature=cfg.TEMPERATURE,
                base_url=cfg.OLLAMA_URL,
                num_ctx=cfg.MAX_CONTEXT_TOKENS,
            )
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {provider}")

    def extract_llm_output(self, response) -> str:
        if hasattr(response, "content"):
            return response.content
        elif isinstance(response, str):
            return response
        elif isinstance(response, dict) and "content" in response:
            return response["content"]
        else:
            raise ValueError(
                "Unknown response format from LLM: {}".format(type(response))
            )


external = External()

if __name__ == "__main__":
    pass
