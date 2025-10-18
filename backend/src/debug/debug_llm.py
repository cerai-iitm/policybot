import logging
import os
import socket
from logging.handlers import RotatingFileHandler
from pathlib import Path

from langchain.globals import set_debug


def test_ollama_ipv6_connection(logger):
    import subprocess

    import requests

    addr = "host.docker.internal"

    try:
        logger.info(f"Testing IPv6 ping to {addr}")
        # Try ping6 first, fallback to ping -6 if ping6 not available
        try:
            result = subprocess.run(
                ["ping6", "-c", "1", addr], capture_output=True, text=True, timeout=5
            )
        except FileNotFoundError:
            logger.warning("ping6 not found, trying ping -6")
            try:
                result = subprocess.run(
                    ["ping", "-6", "-c", "1", addr],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
            except FileNotFoundError:
                logger.error("Neither ping6 nor ping -6 available")
                return

        if result.returncode == 0:
            logger.info(f"IPv6 ping to {addr}: SUCCESS")
        else:
            logger.info(f"IPv6 ping to {addr}: FAILED - {result.stderr}")
    except Exception as e:
        logger.info(f"IPv6 ping to {addr}: FAILED - {e}")

    # Test HTTP connection with IPv6 to host.docker.internal
    url = "http://host.docker.internal:11434/api/version"

    try:
        logger.info(f"Testing HTTP connection to {url}")
        response = requests.get(url, timeout=5)
        logger.info(f"HTTP test to {url}: SUCCESS (status {response.status_code})")
        logger.info(f"Response: {response.text[:200]}...")
    except Exception as e:
        logger.error(f"HTTP test to {url}: FAILED - {e}")


def test_ollama_ipv4_connection(logger):
    """Test IPv4 connection to Ollama on host"""
    import subprocess

    import requests

    # Only test host.docker.internal (the actual target)
    addr = "host.docker.internal"

    try:
        logger.info(f"Testing IPv4 ping to {addr}")
        result = subprocess.run(
            ["ping", "-c", "1", addr], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            logger.info(f"IPv4 ping to {addr}: SUCCESS")
        else:
            logger.info(f"IPv4 ping to {addr}: FAILED - {result.stderr}")
    except Exception as e:
        logger.info(f"IPv4 ping to {addr}: FAILED - {e}")

    # Test HTTP connection to host.docker.internal only
    url = "http://host.docker.internal:11434/api/version"

    try:
        logger.info(f"Testing HTTP connection to {url}")
        response = requests.get(url, timeout=5)
        logger.info(f"HTTP test to {url}: SUCCESS (status {response.status_code})")
        logger.info(f"Response: {response.text[:200]}...")

        # Test additional Ollama endpoints
        base_url = "http://host.docker.internal:11434"

        # Test /api/tags endpoint
        try:
            tags_response = requests.get(f"{base_url}/api/tags", timeout=5)
            logger.info(
                f"Ollama /api/tags test: SUCCESS (status {tags_response.status_code})"
            )
            logger.info(f"Available models: {tags_response.text[:300]}...")
        except Exception as e:
            logger.error(f"Ollama /api/tags test: FAILED - {e}")

        # Test /api/ps endpoint (running models)
        try:
            ps_response = requests.get(f"{base_url}/api/ps", timeout=5)
            logger.info(
                f"Ollama /api/ps test: SUCCESS (status {ps_response.status_code})"
            )
            logger.info(f"Running models: {ps_response.text[:300]}...")
        except Exception as e:
            logger.error(f"Ollama /api/ps test: FAILED - {e}")

    except Exception as e:
        logger.error(f"HTTP test to {url}: FAILED - {e}")

    # Test raw socket connection to host.docker.internal
    try:
        logger.info("Testing raw IPv4 socket connection to host.docker.internal:11434")
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        host_ip = socket.gethostbyname("host.docker.internal")
        logger.info(f"host.docker.internal resolves to: {host_ip}")
        sock.connect((host_ip, 11434))
        logger.info("Raw IPv4 socket connection to host.docker.internal: SUCCESS")
        sock.close()
    except Exception as e:
        logger.error(
            f"Raw IPv4 socket connection to host.docker.internal: FAILED - {e}"
        )


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
        response = llm.invoke(
            "Testing if the Ollama LLM is working. Return 'Ollama respose okay' if you get this prompt."
        )

        logger.info(f"Ollama LLM response recieved: {response}")

    except Exception as e:
        logger.error(f"Error creating or invoking Ollama LLM: {e}")


def get_ollama_llm_ipv6(logger):
    """Test Ollama LLM connection forcing IPv6"""
    import socket

    from langchain_ollama.llms import OllamaLLM

    try:
        addr_info = socket.getaddrinfo("host.docker.internal", 11434, socket.AF_INET6)
        if addr_info:
            ipv6_addr = addr_info[0][4][0]
            base_url = f"http://[{ipv6_addr}]:11434"
            logger.info(f"Forcing IPv6 connection to: {base_url}")
        else:
            raise Exception("No IPv6 address available")

        llm = OllamaLLM(
            model="gemma3n:e4b",
            temperature=0.1,
            base_url=base_url,
            num_ctx=32000,
        )
        logger.info("Ollama LLM instance created")

        logger.info("Invoking Ollama LLM with test prompt")
        response = llm.invoke(
            "Testing Ollama LLM connectivity. Return 'Ollama connection okay' if you get this prompt."
        )

        logger.info(f"Ollama LLM response received: {response}")

    except Exception as e:
        logger.error(f"Error with Ollama LLM: {e}")


def get_gemini_llm(logger):

    from langchain_google_genai import ChatGoogleGenerativeAI

    try:
        api_key = os.getenv("GEMINI_API_KEY", "")

        # Log first 5 characters of API key for debugging
        if api_key:
            logger.info(f"Gemini API key (first 5 chars): {api_key[:5]}...")
        else:
            logger.warning("GEMINI_API_KEY is empty or not set")

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
    test_ollama_ipv4_connection(root_logger)  # Test IPv4 first
    test_ollama_ipv6_connection(root_logger)  # Then IPv6
    get_ollama_llm(root_logger)  # Original IPv4 LLM test
    get_ollama_llm_ipv6(root_logger)  # New IPv6 LLM test
    get_gemini_llm(root_logger)
    check_postgres_health(root_logger)
    log_dns_config(root_logger)
    log_dns_resolution(root_logger)
    log_internet_access(root_logger)
    check_qdrant_http_health(root_logger)
    check_qdrant_http_health(root_logger)
