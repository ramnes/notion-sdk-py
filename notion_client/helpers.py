"""Utility functions for notion-sdk-py."""


from typing import Any, Dict
from urllib.parse import urlparse
from uuid import UUID


def pick(base: Dict[Any, Any], *keys: str) -> Dict[Any, Any]:
    """Return a Dict composed of key value pairs for keys passed as args."""
    return {key: base[key] for key in keys if key in base}


def get_url(obj_id: str) -> str:
    """Return url for the object of given id."""
    uuid = UUID(obj_id).hex
    return "https://notion.so/" + uuid


def get_id(url: str) -> str:
    """Return the id of the object of given url."""
    parsed = urlparse(url)
    if parsed.netloc != "notion.so":
        raise ValueError("Not a valid Notion URL")
    path = parsed.path
    if len(path) < 32:
        raise ValueError("The path in the URL seems to be incorrect.")
    raw_id = path[-32:]
    return str(UUID(raw_id))
