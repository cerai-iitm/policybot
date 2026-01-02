from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_ollama.llms import OllamaLLM

from src.config import cfg
from src.logger import logger


class External:
    """
    Stateless factory class for external service integrations.

    All methods are static - no instantiation needed.
    Provides centralized factory methods for LLM providers and utilities.
    """

    @staticmethod
    def create_llm(model_name: str = cfg.MODEL_NAME):
        """
        Factory method to create a fresh LLM instance for the specified model.

        This method always returns a new instance - no caching.
        Suitable for per-request model selection in multi-user scenarios.

        Args:
            model_name: Model ID to use. If None, uses cfg.MODEL_NAME as default.

        Returns:
            Fresh LLM instance configured for the specified model.

        Raises:
            ValueError: If model not supported or provider misconfigured.
        """
        # Default to configured model if none specified
        if not model_name or not model_name.strip():
            model_name = cfg.MODEL_NAME
            logger.debug(f"No model specified, using default: {model_name}")
        else:
            model_name = model_name.strip()

        # Validate model is supported
        valid_model_ids = [m.get("id") for m in cfg.SUPPORTED_MODELS if m.get("id")]
        valid_model_names = [
            m.get("name") for m in cfg.SUPPORTED_MODELS if m.get("name")
        ]

        if model_name not in valid_model_ids:
            logger.error(
                f"Invalid model requested: '{model_name}'. "
                f"Supported model IDs: {valid_model_ids}"
            )
            raise ValueError(
                f"Model '{model_name}' is not supported. "
                f"Available models: {', '.join(valid_model_ids)}"
            )

        logger.info(
            f"Creating LLM instance for model: {model_name} (provider: {cfg.LLM_PROVIDER})"
        )
        logger.debug(f"Supported models in config: {len(cfg.SUPPORTED_MODELS)} total")

        try:
            llm = External._initialize_llm(model_name)
            if llm is None:
                raise ValueError(
                    f"Failed to initialize LLM for model: {model_name}. "
                    "Check LLM_PROVIDER configuration."
                )

            logger.debug(f"Successfully created {type(llm).__name__} instance")
            return llm

        except ValueError as ve:
            # Re-raise ValueError with context
            logger.error(f"Validation error during LLM creation: {ve}")
            raise
        except Exception as e:
            # Catch any other initialization errors
            logger.error(f"Unexpected error creating LLM for model '{model_name}': {e}")
            raise ValueError(
                f"Failed to create LLM instance for model '{model_name}': {str(e)}"
            ) from e

    @staticmethod
    def _initialize_llm(model_name: str):
        """
        Internal method to initialize LLM based on provider configuration.

        Args:
            model_name: Model ID to initialize.

        Returns:
            Initialized LLM instance.

        Raises:
            ValueError: If provider unknown, API key missing, or model not supported.
        """
        provider = cfg.LLM_PROVIDER.lower()
        logger.debug(f"Initializing LLM with provider: {provider}, model: {model_name}")

        if provider == "gemini":
            api_key = cfg.GEMINI_API_KEY
            if not api_key or not api_key.strip():
                logger.error("GEMINI_API_KEY is missing or empty in configuration")
                raise ValueError(
                    "GEMINI_API_KEY is not set in config. "
                    "Please set the environment variable or update config."
                )

            logger.debug(
                f"Initializing Gemini LLM (model: gemini-2.5-flash, temp: {cfg.TEMPERATURE})"
            )
            try:
                gemini_llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    google_api_key=api_key,
                    temperature=cfg.TEMPERATURE,
                    max_tokens=None,
                    timeout=None,
                    max_retries=2,
                )
                logger.debug("Gemini LLM initialized successfully")
                return gemini_llm
            except Exception as e:
                logger.error(f"Failed to initialize Gemini LLM: {e}")
                raise ValueError(f"Gemini initialization failed: {str(e)}") from e

        elif provider == "ollama":
            models = [x.get("id") for x in cfg.SUPPORTED_MODELS]
            index = models.index(model_name) if model_name in models else -1
            if index == -1:
                logger.error(
                    f"Model '{model_name}' not found in SUPPORTED_MODELS for Ollama. "
                    f"Available: {models}"
                )
                raise ValueError(
                    f"Model '{model_name}' not supported for Ollama provider. "
                    f"Available models: {', '.join(models)}"
                )

            model_config = cfg.SUPPORTED_MODELS[index]
            logger.debug(
                f"Initializing Ollama LLM - "
                f"model: {model_config['id']}, "
                f"temp: {cfg.TEMPERATURE}, "
                f"base_url: {cfg.OLLAMA_URL}, "
                f"context: {cfg.MAX_CONTEXT_TOKENS}"
            )

            try:
                ollama_llm = OllamaLLM(
                    model=model_config["id"],
                    temperature=cfg.TEMPERATURE,
                    base_url=cfg.OLLAMA_URL,
                    num_ctx=cfg.MAX_CONTEXT_TOKENS,
                )
                logger.debug("Ollama LLM initialized successfully")
                return ollama_llm
            except Exception as e:
                logger.error(f"Failed to initialize Ollama LLM: {e}")
                raise ValueError(
                    f"Ollama initialization failed for model '{model_name}': {str(e)}"
                ) from e
        else:
            logger.error(
                f"Unknown LLM_PROVIDER: '{provider}'. Must be 'gemini' or 'ollama'"
            )
            raise ValueError(
                f"Unknown LLM_PROVIDER: '{provider}'. "
                f"Supported providers: 'gemini', 'ollama'"
            )

    @staticmethod
    def extract_llm_output(response) -> str:
        """
        Extract text content from LLM response.

        Handles various response formats from different LLM providers.

        Args:
            response: LLM response in various formats (object, string, dict).

        Returns:
            Extracted text content as string.

        Raises:
            ValueError: If response format is unknown.
        """
        if hasattr(response, "content"):
            logger.debug(
                f"Extracting content from response object (type: {type(response).__name__})"
            )
            return response.content
        elif isinstance(response, str):
            logger.debug("Response is already a string")
            return response
        elif isinstance(response, dict) and "content" in response:
            logger.debug("Extracting content from dictionary response")
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


if __name__ == "__main__":
    pass
