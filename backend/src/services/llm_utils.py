from src.core import cfg, logger


def force_ollama_provider() -> None:
    """Force the runtime LLM provider to 'ollama'.

    This mutates the global cfg object so subsequent LLM_Interface
    initializations use the Ollama provider. Use sparingly.
    """
    try:
        cfg.LLM_PROVIDER = "ollama"
        logger.info("Runtime override: forced cfg.LLM_PROVIDER='ollama'")
    except Exception as e:
        logger.error(f"Failed to force ollama provider override: {e}")
