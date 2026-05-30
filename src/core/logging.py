"""Logging system configuration utilizing thread-safe unified console colored streams."""

import logging

import colorlog

__all__ = ("setup_logging",)


def setup_logging() -> None:
    """Initialize structured and colored terminal logging patterns for production observability."""
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter("%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logging.basicConfig(level=logging.INFO, handlers=[handler])
