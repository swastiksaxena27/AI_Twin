"""Shared logging configuration."""

import logging
from pathlib import Path

from behavioral_guardian.config.settings import LOG_DATE_FORMAT, LOG_FORMAT, LOGS_DIR


def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """Configure and return a module logger with file and console handlers."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    log_file = LOGS_DIR / f"{name.replace('.', '_')}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def ensure_directory(path: Path) -> Path:
    """Create directory if missing and return the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path
