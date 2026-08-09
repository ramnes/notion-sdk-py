"""The async paginator must stop on the same conditions as the sync one."""

import pytest

from notion_client.helpers import async_iterate_paginated_api, iterate_paginated_api


def _pages(pages):
    """A fake endpoint returning the given pages in order."""
    calls = {"n": 0}

    def sync(**kwargs):
        page = pages[min(calls["n"], len(pages) - 1)]
        calls["n"] += 1
        return page

    async def asyncf(**kwargs):
        return sync(**kwargs)

    return sync, asyncf


@pytest.mark.asyncio
async def test_async_paginator_stops_when_has_more_is_absent():
    """A response without has_more stopped sync and raised KeyError on async."""
    sync, asyncf = _pages([{"results": [1], "next_cursor": None}])
    assert list(iterate_paginated_api(sync)) == [1]
    sync, asyncf = _pages([{"results": [1], "next_cursor": None}])
    assert [x async for x in async_iterate_paginated_api(asyncf)] == [1]


@pytest.mark.asyncio
async def test_async_paginator_stops_on_empty_cursor():
    """An empty-string cursor stopped sync and looped forever on async."""
    page = {"results": [1], "has_more": True, "next_cursor": ""}
    sync, asyncf = _pages([page])
    assert list(iterate_paginated_api(sync)) == [1]
    sync, asyncf = _pages([page])
    out = []
    async for x in async_iterate_paginated_api(asyncf):
        out.append(x)
        if len(out) > 3:
            pytest.fail("async paginator did not terminate on an empty cursor")
    assert out == [1]
