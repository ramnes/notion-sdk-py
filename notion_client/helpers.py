"""Utility functions for notion-sdk-py."""

import re
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
)
from urllib.parse import parse_qs, urlparse
from uuid import UUID


def pick(base: Dict[Any, Any], *keys: str) -> Dict[Any, Any]:
    """Return a dict composed of key value pairs for keys passed as args."""
    result = {}
    for key in keys:
        if key not in base:
            continue
        value = base.get(key)
        if value is None and key == "start_cursor":
            continue
        result[key] = value
    return result


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
) -> Generator[Any, None, None]:
    """Return an iterator over the results of any paginated Notion API."""
    next_cursor = kwargs.pop("start_cursor", None)

    while True:
        response = function(**kwargs, start_cursor=next_cursor)
        for result in response.get("results"):
            yield result

        next_cursor = response.get("next_cursor")
        if not response.get("has_more") or not next_cursor:
            return


def collect_paginated_api(function: Callable[..., Any], **kwargs: Any) -> List[Any]:
    """Collect all the results of paginating an API into a list."""
    return [result for result in iterate_paginated_api(function, **kwargs)]


async def async_iterate_paginated_api(
    function: Callable[..., Awaitable[Any]], **kwargs: Any
) -> AsyncGenerator[Any, None]:
    """Return an async iterator over the results of any paginated Notion API."""
    next_cursor = kwargs.pop("start_cursor", None)

    while True:
        response = await function(**kwargs, start_cursor=next_cursor)
        for result in response.get("results"):
            yield result

        next_cursor = response.get("next_cursor")
        if (not response["has_more"]) | (next_cursor is None):
            return


async def async_collect_paginated_api(
    function: Callable[..., Awaitable[Any]], **kwargs: Any
) -> List[Any]:
    """Collect asynchronously all the results of paginating an API into a list."""
    return [result async for result in async_iterate_paginated_api(function, **kwargs)]


def is_full_block(response: Dict[Any, Any]) -> bool:
    """Return `True` if response is a full block."""
    return response.get("object") == "block" and "type" in response


def is_full_page(response: Dict[Any, Any]) -> bool:
    """Return `True` if response is a full page."""
    return response.get("object") == "page" and "url" in response


def is_full_database(response: Dict[Any, Any]) -> bool:
    """Return `True` if response is a full database."""
    return response.get("object") == "database" and "title" in response


def is_full_page_or_database(response: Dict[Any, Any]) -> bool:
    """Return `True` if `response` is a full database or a full page."""
    if response.get("object") == "database":
        return is_full_database(response)
    return is_full_page(response)


def is_full_user(response: Dict[Any, Any]) -> bool:
    """Return `True` if response is a full user."""
    return "type" in response


def is_full_comment(response: Dict[Any, Any]) -> bool:
    """Return `True` if response is a full comment."""
    return "type" in response


def is_text_rich_text_item_response(rich_text: Dict[Any, Any]) -> bool:
    """Return `True` if `rich_text` is a text."""
    return rich_text.get("type") == "text"


def is_equation_rich_text_item_response(rich_text: Dict[Any, Any]) -> bool:
    """Return `True` if `rich_text` is an equation."""
    return rich_text.get("type") == "equation"


def is_mention_rich_text_item_response(rich_text: Dict[Any, Any]) -> bool:
    """Return `True` if `rich_text` is a mention."""
    return rich_text.get("type") == "mention"


def _format_uuid(compact_uuid: str) -> str:
    """Format a compact UUID (32 chars) into standard format with hyphens."""
    if len(compact_uuid) != 32:
        raise ValueError("UUID must be exactly 32 characters")

    return (
        f"{compact_uuid[:8]}-{compact_uuid[8:12]}-{compact_uuid[12:16]}-"
        f"{compact_uuid[16:20]}-{compact_uuid[20:]}"
    )


def extract_notion_id(url_or_id: str) -> Optional[str]:
    """Extract a Notion ID from a Notion URL or return the input if it's already a valid ID.

    Prioritizes path IDs over query parameters to avoid extracting view IDs instead of database IDs.

    Args:
        url_or_id: A Notion URL or ID string

    Returns:
        The extracted UUID in standard format (with hyphens) or None if invalid

    Example:
        >>> # Database URL with view ID - extracts database ID, not view ID
        >>> extract_notion_id('https://notion.so/workspace/DB-abc123def456789012345678901234ab?v=viewid123')
        'abc123de-f456-7890-1234-5678901234ab'  # database ID

        >>> # Already formatted UUID
        >>> extract_notion_id('12345678-1234-1234-1234-123456789abc')
        '12345678-1234-1234-1234-123456789abc'
    """
    if not url_or_id or not isinstance(url_or_id, str):
        return None

    trimmed = url_or_id.strip()

    # Check if it's already a properly formatted UUID
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
    )
    if uuid_pattern.match(trimmed):
        return trimmed.lower()

    # Check if it's a compact UUID (32 chars, no hyphens)
    compact_uuid_pattern = re.compile(r"^[0-9a-f]{32}$", re.IGNORECASE)
    if compact_uuid_pattern.match(trimmed):
        return _format_uuid(trimmed.lower())

    # Try to parse as URL
    try:
        parsed = urlparse(trimmed)

        # Check if it's a valid Notion domain
        valid_domains = ["notion.so", "www.notion.so", "notion.site"]
        if parsed.netloc not in valid_domains:
            return None

        # First, try to extract ID from the path (prioritized)
        path = parsed.path
        if path:
            # Look for 32-character hex strings in the path
            path_id_matches = re.findall(r"[0-9a-f]{32}", path, re.IGNORECASE)
            if path_id_matches:
                # Take the last match (most likely to be the main ID)
                return _format_uuid(path_id_matches[-1].lower())

        # If no path ID found, try query parameters
        query_params = parse_qs(parsed.query)
        for param in ["p", "id"]:
            if param in query_params and query_params[param]:
                candidate = query_params[param][0].strip()
                if compact_uuid_pattern.match(candidate):
                    return _format_uuid(candidate.lower())
                elif uuid_pattern.match(candidate):
                    return candidate.lower()

        # Try fragment (for block IDs)
        if parsed.fragment:
            fragment = parsed.fragment
            # Remove "block-" prefix if present
            if fragment.startswith("block-"):
                fragment = fragment[6:]
            if compact_uuid_pattern.match(fragment):
                return _format_uuid(fragment.lower())

        return None

    except Exception:
        return None


def extract_database_id(url_or_id: str) -> Optional[str]:
    """Extract a database ID from a Notion URL or validate if it's already a valid ID.

    This is an alias for extract_notion_id for clarity when working with databases.

    Args:
        url_or_id: A Notion database URL or ID string

    Returns:
        The extracted UUID in standard format (with hyphens) or None if invalid
    """
    return extract_notion_id(url_or_id)


def extract_page_id(url_or_id: str) -> Optional[str]:
    """Extract a page ID from a Notion URL or validate if it's already a valid ID.

    This is an alias for extract_notion_id for clarity when working with pages.

    Args:
        url_or_id: A Notion page URL or ID string

    Returns:
        The extracted UUID in standard format (with hyphens) or None if invalid
    """
    return extract_notion_id(url_or_id)


def extract_block_id(url_or_id: str) -> Optional[str]:
    """Extract a block ID from a Notion URL fragment or validate if it's already a valid ID.

    Specifically looks for block IDs in URL fragments (after #).
    If no fragment is present, falls back to extract_notion_id behavior.

    Args:
        url_or_id: A Notion URL with block fragment or ID string

    Returns:
        The extracted UUID in standard format (with hyphens) or None if invalid
    """
    if not url_or_id or not isinstance(url_or_id, str):
        return None

    # If it looks like a URL, try to extract from fragment first
    if "://" in url_or_id:
        try:
            parsed = urlparse(url_or_id.strip())
            if parsed.fragment:
                fragment = parsed.fragment
                # Remove "block-" prefix if present
                if fragment.startswith("block-"):
                    fragment = fragment[6:]

                # Check if it's a compact UUID
                compact_uuid_pattern = re.compile(r"^[0-9a-f]{32}$", re.IGNORECASE)
                if compact_uuid_pattern.match(fragment):
                    return _format_uuid(fragment.lower())

                # Check if it's already formatted UUID
                uuid_pattern = re.compile(
                    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
                    re.IGNORECASE,
                )
                if uuid_pattern.match(fragment):
                    return fragment.lower()

            # If no valid fragment found, return None (block IDs should be in fragments)
            return None
        except Exception:
            pass

    # Fall back to general ID extraction for non-URL inputs
    return extract_notion_id(url_or_id)
