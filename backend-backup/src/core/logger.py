import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import structlog


def setup_logger() -> None:
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        # TODO: convert to IST Format later
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]

    # Determine a writable log directory. Prefer a local 'logs' directory, but fall back to '/tmp' if permission denied.
    log_dir = Path("logs")
    try:
        log_dir.mkdir(exist_ok=True)
    except Exception as e:
        # Fallback to a guaranteed writable temp directory
        log_dir = Path("/tmp")
        # Ensure the fallback directory exists (usually does)
        log_dir.mkdir(parents=True, exist_ok=True)

    handlers = []
    # JSON file handler (optional)
    try:
        json_file_handler = RotatingFileHandler(
            log_dir / "app_logs.jsonl", maxBytes=10 * 1024 * 1024, backupCount=3
        )
        json_file_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processor=structlog.processors.JSONRenderer(),
            )
        )
        handlers.append(json_file_handler)
    except Exception:
        # If file creation fails, skip JSON logging
        pass

    # Plain text file handler (optional)
    try:
        text_file_handler = RotatingFileHandler(
            log_dir / "app.log", maxBytes=10 * 1024 * 1024, backupCount=3
        )
        text_file_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processor=structlog.dev.ConsoleRenderer(
                    colors=False
                ),  # No colors in text files
            )
        )
        handlers.append(text_file_handler)
    except Exception:
        pass

    # Console handler (always used)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(colors=True),
        )
    )
    handlers.append(console_handler)

    root_logger = logging.getLogger()
    root_logger.handlers = handlers
    root_logger.setLevel(logging.INFO)

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


setup_logger()
logger = structlog.get_logger()


if __name__ == "__main__":
    pass
