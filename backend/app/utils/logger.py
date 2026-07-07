"""
ApplyMate AI – Centralized Logger
Uses loguru for structured, colorized logging with DB sink support.
"""

import sys
from loguru import logger as _loguru_logger


def get_logger(name: str):
    """Return a loguru logger bound to a module name."""
    return _loguru_logger.bind(module=name)


def setup_logging(debug: bool = False) -> None:
    """Configure loguru sinks on app startup."""
    _loguru_logger.remove()

    level = "DEBUG" if debug else "INFO"

    # Console sink
    _loguru_logger.add(
        sys.stdout,
        level=level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[module]}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # File sink with rotation
    _loguru_logger.add(
        "logs/applymate.log",
        level="INFO",
        rotation="10 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[module]} | {message}",
        catch=True,
    )

    _loguru_logger.bind(module="logger").info("Logging initialized")
