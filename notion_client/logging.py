"""Custom logging for notion-sdk-py."""

import logging
from logging import Logger


def make_console_logger() -> Logger:
    """Return a custom logger."""
    logger = logging.getLogger(__package__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(logging.BASIC_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
