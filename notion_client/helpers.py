"""Utility functions for notion-sdk-py."""

from typing import Any, Dict


def pick(base: Dict[Any, Any], *keys: str) -> Dict[Any, Any]:
    """Return a Dict composed of key value pairs for keys passed as args."""
    return {key: base[key] for key in keys if key in base}
