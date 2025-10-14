import logging
import os
import socket
from logging.handlers import RotatingFileHandler
from pathlib import Path

from langchain.globals import set_debug


def get_ollama_llm(logger):

    from langchain_ollama.llms import OllamaLLM

    try:
        logger.info("Creating Ollama LLM instance")
        llm = OllamaLLM(
            model="gemma3n:e4b",
            temperature=0.1,
            base_url="http://host.docker.internal:11434",
            num_ctx=32000,
        )
        logger.info("Ollama LLM instance created")

        logger.info("Invoking Ollama LLM with test prompt")
        resposne = llm.invoke(
            "Testing if the Ollama LLM is working. Return 'Ollama respose okay' if you get this prompt."
        )

        logger.info(f"Ollama LLM response recieved: {resposne}")

    except Exception as e:
        logger.error(f"Error creating or invoking Ollama LLM: {e}")


def get_gemini_llm(logger):

    from langchain_google_genai import ChatGoogleGenerativeAI

    try:
        api_key = os.getenv("GEMINI_API_KEY", "")
        logger.info("Creating Gemini LLM instance")
        gemini_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.1,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            verbose=True,
        )
        logger.info("Gemini LLM instance created")

        logger.info("Invoking Gemini LLM with test prompt")
        response = gemini_llm.invoke(
            "Testing if the Gemini LLM is working. Return 'Gemini Response Okay' if you get this prompt."
        )
        logger.info(f"Gemini LLM response received: {response}")
        logger.info("Response content: {}".format(response.content))
    except Exception as e:
        logger.error(f"Error creating or invoking Gemini LLM: {e}")


def check_postgres_health(logger):
    from sqlalchemy import create_engine

    DB_HOST = "postgres_db"
    DATABASE_URL = f"postgresql+psycopg2://postgres:postgres@{DB_HOST}:5432/policybot"
    engine = create_engine(DATABASE_URL)

    try:
        from sqlalchemy import text

        logger.info("Checking Postgres database connection")

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Postgres health check: OK")
    except Exception as e:
        logger.error(f"Postgres health check failed: {e}")


def log_dns_config(logger):
    try:
        logger.info("Reading /etc/resolv.conf for DNS configuration")
        with open("/etc/resolv.conf") as f:
            dns_info = f.read()
        logger.info(f"DNS config (/etc/resolv.conf):\n{dns_info}")
    except Exception as e:
        logger.error(f"Could not read /etc/resolv.conf: {e}")


def log_dns_resolution(logger):
    test_domains = [
        "www.google.com",
        "www.cloudflare.com",
        "www.github.com",
    ]
    for domain in test_domains:
        try:
            logger.info(f"Resolving DNS for {domain}")
            ip = socket.gethostbyname(domain)
            logger.info(f"DNS resolution for {domain}: {ip}")
        except Exception as e:
            logger.error(f"DNS resolution for {domain}: FAILED ({e})")


def log_internet_access(logger):
    import requests

    test_urls = [
        "https://www.google.com",
        "https://1.1.1.1",
        "https://8.8.8.8",
    ]
    for url in test_urls:
        try:
            logger.info(f"Testing internet access to {url}")
            resp = requests.get(url, timeout=5)
            logger.info(
                f"Internet access test to {url}: SUCCESS (status {resp.status_code})"
            )
        except Exception as e:
            logger.error(f"Internet access test to {url}: FAILED ({e})")


def check_qdrant_http_health(logger):
    import requests

    try:
        resp = requests.get("http://qdrant:6333/healthz")
        try:
            logger.info(f"Qdrant HTTP health: {resp.json()}")
        except Exception:
            logger.info(f"Qdrant HTTP health (raw): {resp.text}")
    except Exception as e:
        logger.error(f"Qdrant HTTP health check failed: {e}")


if __name__ == "__main__":
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_dir / "debug_test.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    set_debug(True)
    get_ollama_llm(root_logger)
    get_gemini_llm(root_logger)
    check_postgres_health(root_logger)
    log_dns_config(root_logger)
    log_dns_resolution(root_logger)
    log_internet_access(root_logger)
    check_qdrant_http_health(root_logger)
