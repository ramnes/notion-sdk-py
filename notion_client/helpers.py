"""Utility functions for notion-sdk-py."""
from typing import Any, Dict, List
from urllib.parse import urlparse
from uuid import UUID


def pick(base: Dict[Any, Any], *keys: str, keys_to_keep_if_none: List[str]=[]) -> Dict[Any, Any]:
    """Return a dict composed of key value pairs for keys passed as args."""
    body = {key: base[key] for key in keys if key in base}

    keys_none = [key for key in body if body[key] is None]
    for key_none in keys_none:
        if key_none not in keys_to_keep_if_none:
            body.pop(key_none)

    return body


def get_url(object_id: str) -> str:
    """Return the URL for the object with the given id."""
    return "https://notion.so/" + UUID(object_id).hex


def get_id(url: str) -> str:
    """Return the id of the object behind the given URL."""
    parsed = urlparse(url)
    if parsed.netloc not in ("notion.so", "www.notion.so"):
        raise ValueError("Not a valid Notion URL.")
    path = parsed.path
    if len(path) < 32:
        raise ValueError("The path in the URL seems to be incorrect.")
    raw_id = path[-32:]
    return str(UUID(raw_id))
