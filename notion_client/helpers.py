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
from urllib.parse import urlparse
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


def is_full_data_source(response: Dict[Any, Any]) -> bool:
    """* Return `true` if `response` is a full data source."""
    return response.get("object") == "data_source"


def is_full_database(response: Dict[Any, Any]) -> bool:
    """Return `True` if response is a full database."""
    return response.get("object") == "database" and "title" in response


def is_full_page_or_data_source(response: Dict[Any, Any]) -> bool:
    """Return `True` if `response` is a full database or a full page."""
    if response.get("object") == "data_source":
        return is_full_data_source(response)
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

    Returns the extracted UUID in standard format (with hyphens) or None if invalid.

    ```python
    # Database URL with view ID - extracts database ID, not view ID
    extract_notion_id('https://notion.so/workspace/DB-abc123def456789012345678901234ab?v=viewid123')
    # Returns: 'abc123de-f456-7890-1234-5678901234ab'  # database ID

    # Already formatted UUID
    extract_notion_id('12345678-1234-1234-1234-123456789abc')
    # Returns: '12345678-1234-1234-1234-123456789abc'
    ```
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

    # For URLs, check if it's a valid Notion domain
    if "://" in trimmed:
        if not re.search(r"://(?:www\.)?notion\.(?:so|site)/", trimmed, re.IGNORECASE):
            return None

    # Fallback to query parameters if no direct ID found
    query_match = re.search(
        r"[?&](?:p|page_id|database_id)=([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|[0-9a-f]{32})",
        trimmed,
        re.IGNORECASE,
    )
    if query_match:
        match_str = query_match.group(1).lower()
        return match_str if "-" in match_str else _format_uuid(match_str)

    # Last resort: any 32-char hex string in the URL
    any_match = re.search(r"([0-9a-f]{32})", trimmed, re.IGNORECASE)
    if any_match:
        return _format_uuid(any_match.group(1).lower())

    return None


def extract_database_id(database_url: str) -> Optional[str]:
    """Extract a database ID from a Notion URL or validate if it's already a valid ID.

    This is an alias for `extract_notion_id` for clarity when working with databases.

    Returns the extracted UUID in standard format (with hyphens) or None if invalid.
    """
    return extract_notion_id(database_url)


def extract_page_id(page_url: str) -> Optional[str]:
    """Extract a page ID from a Notion URL or validate if it's already a valid ID.

    This is an alias for `extract_notion_id` for clarity when working with pages.

    Returns the extracted UUID in standard format (with hyphens) or None if invalid.
    """
    return extract_notion_id(page_url)


def extract_block_id(url_or_id: str) -> Optional[str]:
    """Extract a block ID from a Notion URL fragment or validate if it's already a valid ID.

    Specifically looks for block IDs in URL fragments (after #).
    If no fragment is present, falls back to `extract_notion_id` behavior.

    Returns the extracted UUID in standard format (with hyphens) or None if invalid.
    """
    if not url_or_id or not isinstance(url_or_id, str):
        return None

    # Look for block fragment in URL (#block-32chars or just #32chars or #formatted-uuid)
    block_match = re.search(
        r"#(?:block-)?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|[0-9a-f]{32})",
        url_or_id,
        re.IGNORECASE,
    )
    if block_match:
        match_str = block_match.group(1).lower()
        # If it's already formatted, return as is; otherwise format it
        return match_str if "-" in match_str else _format_uuid(match_str)

    # Fall back to general ID extraction for non-URL inputs
    return extract_notion_id(url_or_id)


def iterate_data_source_templates(
    function: Callable[..., Any], **kwargs: Any
) -> Generator[Any, None, None]:
    """Return an iterator over templates from a data source.

    Example:

    ```python
    for template in iterate_data_source_templates(
        client.data_sources.list_templates,
        data_source_id=data_source_id,
    ):
        print(template["name"], template["is_default"])
    ```
    """
    next_cursor = kwargs.pop("start_cursor", None)

    while True:
        response = function(**kwargs, start_cursor=next_cursor)
        for template in response.get("templates", []):
            yield template

        next_cursor = response.get("next_cursor")
        if not response.get("has_more") or not next_cursor:
            return


def collect_data_source_templates(
    function: Callable[..., Any], **kwargs: Any
) -> List[Any]:
    """Collect all templates from a data source into a list.

    Example:

    ```python
    templates = collect_data_source_templates(
        client.data_sources.list_templates,
        data_source_id=data_source_id,
    )
    # Do something with templates.
    ```
    """
    return [template for template in iterate_data_source_templates(function, **kwargs)]


async def async_iterate_data_source_templates(
    function: Callable[..., Awaitable[Any]], **kwargs: Any
) -> AsyncGenerator[Any, None]:
    """Return an async iterator over templates from a data source.

    Example:

    ```python
    async for template in async_iterate_data_source_templates(
        async_client.data_sources.list_templates,
        data_source_id=data_source_id,
    ):
        print(template["name"], template["is_default"])
    ```
    """
    next_cursor = kwargs.pop("start_cursor", None)

    while True:
        response = await function(**kwargs, start_cursor=next_cursor)
        for template in response.get("templates", []):
            yield template

        next_cursor = response.get("next_cursor")
        if not response.get("has_more") or not next_cursor:
            return


async def async_collect_data_source_templates(
    function: Callable[..., Awaitable[Any]], **kwargs: Any
) -> List[Any]:
    """Collect asynchronously all templates from a data source into a list.

    Example:

    ```python
    templates = await async_collect_data_source_templates(
        async_client.data_sources.list_templates,
        data_source_id=data_source_id,
    )
    # Do something with templates.
    ```
    """
    return [
        template
        async for template in async_iterate_data_source_templates(function, **kwargs)
    ]
