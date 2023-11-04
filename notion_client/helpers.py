"""Utility functions for notion-sdk-py."""
from typing import Any, AsyncGenerator, Awaitable, Callable, Dict, Generator, List
from urllib.parse import urlparse
from uuid import UUID


def pick(base: Dict[Any, Any], *keys: str) -> Dict[Any, Any]:
    """Return a dict composed of key value pairs for keys passed as args."""
    return {key: base[key] for key in keys if key in base and base[key] is not None}


def get_url(object_id: str) -> str:
    """Return the URL for the object with the given id."""
    return f"https://notion.so/{UUID(object_id).hex}"


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


def iterate_paginated_api(
    function: Callable[..., Any], **kwargs: Any
) -> Generator[List[Any], None, None]:
    """Return an iterator over the results of any paginated Notion API."""
    next_cursor = None

    while True:
        response = function(**kwargs, start_cursor=next_cursor)
        yield response.get("results")

        next_cursor = response.get("next_cursor")
        if not response.get("has_more") or not next_cursor:
            return


def collect_paginated_api(function: Callable[..., Any], **kwargs: Any) -> List[Any]:
    """Collect all the results of paginating an API into a list."""
    results = []
    for partial_res in iterate_paginated_api(function, **kwargs):
        results += partial_res
    return results


async def async_iterate_paginated_api(
    function: Callable[..., Awaitable[Any]], **kwargs: Any
) -> AsyncGenerator[List[Any], None]:
    """Return an async iterator over the results of any paginated Notion API."""
    next_cursor = None

    while True:
        response = await function(**kwargs, start_cursor=next_cursor)
        yield response.get("results")

        next_cursor = response.get("next_cursor")
        if (not response["has_more"]) | (next_cursor is None):
            return


async def async_collect_paginated_api(
    function: Callable[..., Awaitable[Any]], **kwargs: Any
) -> List[Any]:
    """Collect asynchronously all the results of paginating an API into a list."""
    results = []
    async for partial_res in async_iterate_paginated_api(function, **kwargs):
        results += partial_res
    return results


def is_full_block(response: Dict[Any, Any]) -> bool:
    """Return `true` if response is a full block."""
    return response.get("object") == "block" and "type" in response


def is_full_page(response: Dict[Any, Any]) -> bool:
    """Return `true` if response is a full page."""
    return response.get("object") == "page" and "url" in response


def is_full_database(response: Dict[Any, Any]) -> bool:
    """Return `true` if response is a full database."""
    return response.get("object") == "database" and "title" in response


def is_full_page_or_database(response: Dict[Any, Any]) -> bool:
    """Return `true` if `response` is a full database or a full page."""
    if response.get("object") == "database":
        return is_full_database(response)
    return is_full_page(response)


def is_full_user(response: Dict[Any, Any]) -> bool:
    """Return `true` if response is a full user."""
    return "type" in response


def is_full_comment(response: Dict[Any, Any]) -> bool:
    """Return `true` if response is a full comment."""
    return "type" in response
