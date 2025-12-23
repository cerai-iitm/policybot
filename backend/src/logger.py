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

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    json_file_handler = RotatingFileHandler(
       log_dir / "app_logs.jsonl", maxBytes=10*1024*1024, backupCount=3
    )
    json_file_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
        )
    )

    text_file_handler = RotatingFileHandler(
        log_dir / "app.log", maxBytes=10*1024*1024, backupCount=3
    )
    text_file_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(colors=False), # No colors in text files
        )
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(colors=True),
        )
    )

    root_logger = logging.getLogger()
    root_logger.handlers = [json_file_handler, text_file_handler, console_handler]
    root_logger.setLevel(logging.INFO)

    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


setup_logger()
logger = structlog.get_logger()



if __name__ == "__main__":
    pass
