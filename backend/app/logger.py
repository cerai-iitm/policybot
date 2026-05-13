# backend/app/logger.py
import logging
import logging.handlers
import sys
from pathlib import Path

import structlog
from structlog.dev import ConsoleRenderer
from structlog.processors import (
    JSONRenderer,
    StackInfoRenderer,
    TimeStamper,
    add_log_level,
    format_exc_info,
)
from structlog.stdlib import BoundLogger, LoggerFactory, ProcessorFormatter


def configure_logging(
    *,
    log_dir: str | Path = "logs",
    human_logfile: str = "app.log",
    structured_logfile: str = "app_structured.jsonl",
    level: int = logging.DEBUG,
    console_colors: bool = True,
) -> None:
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    human_path = log_dir / human_logfile
    structured_path = log_dir / structured_logfile

    pre_processors = [
        add_log_level,
        TimeStamper(fmt="iso"),
        StackInfoRenderer(),
        format_exc_info,
    ]

    console_renderer = ProcessorFormatter(
        processor=ConsoleRenderer(colors=console_colors),
        foreign_pre_chain=pre_processors,
    )

    json_renderer = ProcessorFormatter(
        processor=JSONRenderer(sort_keys=True),
        foreign_pre_chain=pre_processors,
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    # Console
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(console_renderer)
    root_logger.addHandler(ch)

    # Human file
    fh = logging.handlers.RotatingFileHandler(
        filename=str(human_path),
        maxBytes=10 * 1024 * 1024,
        backupCount=7,
        encoding="utf-8",
    )
    fh.setLevel(level)
    fh.setFormatter(console_renderer)
    root_logger.addHandler(fh)

    # Structured file (JSONL)
    sh = logging.handlers.RotatingFileHandler(
        filename=str(structured_path),
        maxBytes=50 * 1024 * 1024,
        backupCount=10,
        encoding="utf-8",
    )
    sh.setLevel(level)
    sh.setFormatter(json_renderer)
    root_logger.addHandler(sh)

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=LoggerFactory(),
        wrapper_class=BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("qdrant_client").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> logging.Logger:
    return logging.getLogger(name)
