import logging
import os


def get_logger(name: str) -> logging.Logger:
    """Return a logger configured from VIBEVOX_LOG_LEVEL env var (default: WARNING)."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        level = os.environ.get("VIBEVOX_LOG_LEVEL", "WARNING").upper()
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, level, logging.WARNING))
    return logger
