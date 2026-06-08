"""Small logging helper for the safe simulator."""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

from settings import LOG_CONSOLE_ENABLED, LOG_DIR, LOG_FILE_BACKUP_COUNT, LOG_FILE_ENABLED, LOG_FILE_MAX_SIZE, LOG_LEVEL


def setup_logger(name: str, level: int | None = None) -> logging.Logger:
    """Return a configured logger without adding duplicate handlers."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    resolved_level = level or getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(resolved_level)
    logger.propagate = False

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    if LOG_CONSOLE_ENABLED:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(resolved_level)
        logger.addHandler(console_handler)

    if LOG_FILE_ENABLED:
        log_dir = Path(LOG_DIR)
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{name}.log",
            maxBytes=LOG_FILE_MAX_SIZE,
            backupCount=LOG_FILE_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    if not logger.handlers:
        logger.addHandler(logging.NullHandler())
    return logger
