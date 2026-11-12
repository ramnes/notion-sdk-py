"""Type-only checks, verified by mypy (not executed by pytest).

`assert_type` requires an exact match, so these fail if a result degrades to `Any`.
The negative case relies on `warn_unused_ignores`.
"""

from typing import Any, Dict

from typing_extensions import assert_type

from notion_client import AsyncClient, Client


def sync_cases(c: Client) -> None:
    assert_type(c.search(), Dict[str, Any])
    assert_type(c.blocks.children.list(block_id="b"), Dict[str, Any])


async def async_cases(c: AsyncClient) -> None:
    assert_type(await c.search(), Dict[str, Any])
    assert_type(await c.blocks.children.list(block_id="b"), Dict[str, Any])


async def missing_await(c: AsyncClient) -> None:
    # Not awaited: indexing a coroutine/awaitable must be an error.
    c.search()["results"]  # type: ignore[index]
