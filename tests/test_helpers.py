from types import AsyncGeneratorType, GeneratorType
from unittest.mock import AsyncMock, MagicMock

import pytest

from notion_client.helpers import (
    async_collect_all_data_source_rows,
    async_collect_data_source_templates,
    async_collect_paginated_api,
    async_iterate_all_data_source_rows,
    async_iterate_data_source_templates,
    async_iterate_paginated_api,
    collect_all_data_source_rows,
    collect_data_source_templates,
    collect_paginated_api,
    extract_block_id,
    extract_database_id,
    extract_notion_id,
    extract_page_id,
    get_id,
    get_url,
    is_equation_rich_text_item_response,
    is_full_block,
    is_full_comment,
    is_full_database,
    is_full_data_source,
    is_full_page,
    is_full_page_or_data_source,
    is_full_user,
    is_mention_rich_text_item_response,
    is_text_rich_text_item_response,
    iterate_all_data_source_rows,
    iterate_data_source_templates,
    iterate_paginated_api,
    pick,
)


def test_pick():
    my_dict = {
        "Product": "Notion",
        "API": 2021,
        "python-sdk": "ramnes",
        "optional-variable": None,
    }
    assert pick(my_dict, "Product") == {"Product": "Notion"}
    assert pick(my_dict, "API", "python-sdk") == {
        "API": 2021,
        "python-sdk": "ramnes",
    }
    assert pick(my_dict, "optional-variable") == {"optional-variable": None}
    assert pick(my_dict, "start_cursor") == {}


def test_get_id():
    page_url = "https://notion.so/aahnik/Aahnik-Daw-621cc4c1ad324159bcea215ce18e03a8"
    page_id = "621cc4c1-ad32-4159-bcea-215ce18e03a8"
    db_url = "https://notion.so/aahnik/99572135464649bd95a14ff08f79c7a5?\
            v=f41969f937614159857f6a5725990649"
    db_id = "99572135-4646-49bd-95a1-4ff08f79c7a5"
    assert get_id(page_url) == page_id
    assert get_id(f"{page_url}/") == page_id
    assert get_id(db_url) == db_id
    with pytest.raises(ValueError):
        get_id("https://example.com")
    with pytest.raises(ValueError):
        get_id("https://notion.so/123")
    with pytest.raises(ValueError):
        get_id("https://notion.so/99572135464649b-d95a14ff08f79c7a5")


def test_get_url():
    dashed_id = "540f8e2b-7991-4654-ba10-3c5d8a03e10e"
    obj_id = "540f8e2b79914654ba103c5d8a03e10e"
    url = "https://notion.so/540f8e2b79914654ba103c5d8a03e10e"
    assert get_url(dashed_id) == url
    assert get_url(obj_id) == url
    with pytest.raises(ValueError):
        get_url("540f8e2b799-14654ba103c5d8a03-e10e")
        get_url("123abc")


@pytest.mark.vcr()
def test_iterate_paginated_api(client, page_id):
    children = [
        {"paragraph": {"rich_text": [{"text": {"content": f"paragraph {i}"}}]}}
        for i in range(5)
    ]
    client.blocks.children.append(block_id=page_id, children=children)

    generator = iterate_paginated_api(
        client.blocks.children.list, block_id=page_id, page_size=2
    )
    assert isinstance(generator, GeneratorType)
    results = [result for result in generator]
    assert len(results) == 5

    for result in results:
        client.blocks.delete(block_id=result["id"])

    generator = iterate_paginated_api(
        client.blocks.children.list, block_id=page_id, page_size=2
    )
    assert isinstance(generator, GeneratorType)
    results = [result for result in generator]
    assert len(results) == 0


@pytest.mark.vcr()
def test_collect_paginated_api(client):
    function = client.search
    results = collect_paginated_api(function)

    assert isinstance(results, list)
    assert results != []

    results_empty = collect_paginated_api(function, query="This should have no results")
    assert results_empty == []


@pytest.mark.vcr()
async def test_async_iterate_paginated_api(async_client, async_page_id):
    page_id = async_page_id
    children = [
        {"paragraph": {"rich_text": [{"text": {"content": f"paragraph {i}"}}]}}
        for i in range(5)
    ]
    await async_client.blocks.children.append(block_id=page_id, children=children)

    generator = async_iterate_paginated_api(
        async_client.blocks.children.list, block_id=page_id, page_size=2
    )
    assert isinstance(generator, AsyncGeneratorType)
    results = [result async for result in generator]
    assert len(results) == 5

    for result in results:
        await async_client.blocks.delete(block_id=result["id"])

    generator = async_iterate_paginated_api(
        async_client.blocks.children.list, block_id=page_id, page_size=2
    )
    assert isinstance(generator, AsyncGeneratorType)
    results = [result async for result in generator]
    assert len(results) == 0


@pytest.mark.vcr()
async def test_async_collect_paginated_api(async_client):
    function = async_client.search
    results = await async_collect_paginated_api(function)

    assert isinstance(results, list)
    assert results != []

    results_empty = await async_collect_paginated_api(
        function, query="This should have no results"
    )
    assert results_empty == []


@pytest.mark.vcr()
def test_is_full_block(client, block_id):
    response = client.blocks.retrieve(block_id=block_id)
    assert is_full_block(response)


@pytest.mark.vcr()
def test_is_full_page(client, page_id):
    response = client.pages.retrieve(page_id=page_id)
    assert is_full_page(response)


@pytest.mark.vcr()
def test_is_full_data_source(client, data_source_id):
    response = client.data_sources.retrieve(data_source_id=data_source_id)
    assert is_full_data_source(response)


@pytest.mark.vcr()
def test_is_full_database(client, database_id):
    response = client.databases.retrieve(database_id=database_id)
    assert is_full_database(response)


@pytest.mark.vcr()
def test_is_full_page_or_data_source(client, data_source_id, page_id):
    response = client.pages.retrieve(page_id=page_id)
    assert is_full_page_or_data_source(response)

    response = client.data_sources.retrieve(data_source_id=data_source_id)
    assert is_full_page_or_data_source(response)


@pytest.mark.vcr()
def test_is_full_user(client):
    response = client.users.me()
    assert is_full_user(response)


@pytest.mark.vcr()
def test_is_full_comment(client, page_id, comment_id):
    response = client.comments.list(block_id=page_id)
    assert is_full_comment(response)


@pytest.mark.vcr()
def test_is_text_rich_text_item_response(client, text_block_id):
    response = client.blocks.retrieve(block_id=text_block_id)
    assert is_text_rich_text_item_response(response["paragraph"]["rich_text"][0])


@pytest.mark.vcr()
def test_is_equation_rich_text_item_response(client, equation_block_id):
    response = client.blocks.retrieve(block_id=equation_block_id)
    assert is_equation_rich_text_item_response(response["paragraph"]["rich_text"][0])


@pytest.mark.vcr()
def test_is_mention_rich_text_item_response(client, mention_block_id):
    response = client.blocks.retrieve(block_id=mention_block_id)
    assert is_mention_rich_text_item_response(response["paragraph"]["rich_text"][0])


def test_extract_notion_id_with_standard_urls():
    examples = [
        {
            "url": "https://www.notion.so/myworkspace/My-Database-abc123def456789012345678901234ab",
            "expected": "abc123de-f456-7890-1234-5678901234ab",
        },
        {
            "url": "https://notion.site/Database-Name-123456781234123412341234567890ab",
            "expected": "12345678-1234-1234-1234-1234567890ab",
        },
    ]

    for example in examples:
        assert extract_notion_id(example["url"]) == example["expected"]


def test_extract_notion_id_prioritizes_path_over_query():
    """Test that path ID is prioritized over query parameters."""
    # This is the key fix - database ID in path should be extracted, not view ID in query
    url = "https://notion.so/workspace/MyDB-abc123def456789012345678901234ab?v=def456789012345678901234abcdef12"
    result = extract_notion_id(url)
    assert result == "abc123de-f456-7890-1234-5678901234ab"  # DB ID, not view ID


def test_extract_notion_id_uses_query_when_no_path_id():
    """Test using query parameters when no path ID is available."""
    url = "https://notion.so/share?p=abc123def456789012345678901234ab"
    result = extract_notion_id(url)
    assert result == "abc123de-f456-7890-1234-5678901234ab"


def test_extract_notion_id_handles_formatted_uuids():
    uuid = "12345678-1234-1234-1234-123456789abc"
    assert extract_notion_id(uuid) == "12345678-1234-1234-1234-123456789abc"


def test_extract_notion_id_formats_compact_uuids():
    compact_uuid = "123456781234123412341234567890ab"
    assert extract_notion_id(compact_uuid) == "12345678-1234-1234-1234-1234567890ab"


def test_extract_notion_id_returns_none_for_invalid_inputs():
    invalid_inputs = ["", "not-a-url", "12345", None]
    for invalid_input in invalid_inputs:
        assert extract_notion_id(invalid_input) is None


def test_extract_notion_id_handles_different_domains():
    test_id = "abc123def456789012345678901234ab"
    expected = "abc123de-f456-7890-1234-5678901234ab"

    domains = [
        "https://notion.so/Page-" + test_id,
        "https://www.notion.so/Page-" + test_id,
        "https://notion.site/Page-" + test_id,
    ]

    for url in domains:
        assert extract_notion_id(url) == expected


def test_extract_notion_id_rejects_invalid_domains():
    invalid_urls = [
        "https://google.com/123456781234123412341234567890ab",
        "https://example.com/Page-abc123def456789012345678901234ab",
    ]

    for url in invalid_urls:
        assert extract_notion_id(url) is None


def test_extract_database_id():
    url = "https://www.notion.so/Tasks-abc123def456789012345678901234ab"
    assert extract_database_id(url) == "abc123de-f456-7890-1234-5678901234ab"


def test_extract_page_id():
    url = "https://www.notion.so/My-Page-123456781234123412341234567890ab"
    assert extract_page_id(url) == "12345678-1234-1234-1234-1234567890ab"


def test_extract_block_id_from_fragment():
    url = "https://www.notion.so/Page#block-def456789012345678901234abcdef12"
    assert extract_block_id(url) == "def45678-9012-3456-7890-1234abcdef12"


def test_extract_block_id_without_block_prefix():
    url = "https://www.notion.so/Page#def456789012345678901234abcdef12"
    assert extract_block_id(url) == "def45678-9012-3456-7890-1234abcdef12"


def test_extract_block_id_returns_none_without_fragment():
    assert extract_block_id("https://www.notion.so/Page") is None


def test_extract_block_id_fallback_to_general():
    uuid = "12345678-1234-1234-1234-123456789abc"
    assert extract_block_id(uuid) == "12345678-1234-1234-1234-123456789abc"


def test_extract_notion_id_case_insensitive():
    test_cases = [
        "ABC123DEF456789012345678901234AB",
        "abc123def456789012345678901234ab",
        "AbC123dEf456789012345678901234Ab",
    ]
    expected = "abc123de-f456-7890-1234-5678901234ab"

    for test_id in test_cases:
        assert extract_notion_id(test_id) == expected


def test_extract_notion_id_with_mixed_case_uuid():
    mixed_case_uuid = "12345678-1234-1234-1234-123456789ABC"
    expected = "12345678-1234-1234-1234-123456789abc"
    assert extract_notion_id(mixed_case_uuid) == expected


def test_extract_notion_id_with_whitespace():
    uuid_with_whitespace = "  12345678-1234-1234-1234-123456789abc  "
    expected = "12345678-1234-1234-1234-123456789abc"
    assert extract_notion_id(uuid_with_whitespace) == expected


def test_extract_notion_id_with_query_id_param():
    url = "https://notion.so/share?id=abc123def456789012345678901234ab"
    expected = "abc123de-f456-7890-1234-5678901234ab"
    assert extract_notion_id(url) == expected


def test_extract_notion_id_with_malformed_url():
    """Test handling malformed URLs that cause parsing exceptions."""
    # These should not crash and return None
    malformed_urls = [
        "https://notion.so/[invalid-url-chars]",
        "not-a-url-at-all",
        "",
        None,
    ]
    for url in malformed_urls:
        result = extract_notion_id(url)
        assert result is None, f"Expected None for {url}, got {result}"


def test_extract_notion_id_with_formatted_uuid_in_query():
    url = "https://notion.so/share?p=12345678-1234-1234-1234-123456789abc"
    expected = "12345678-1234-1234-1234-123456789abc"
    assert extract_notion_id(url) == expected


def test_extract_notion_id_with_fragment_fallback():
    url = "https://www.notion.so/Page#abc123def456789012345678901234ab"
    expected = "abc123de-f456-7890-1234-5678901234ab"
    assert extract_notion_id(url) == expected


def test_format_uuid_error_handling():
    """Test _format_uuid function error cases."""
    from notion_client.helpers import _format_uuid

    # Test invalid length
    try:
        _format_uuid("tooshort")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "32 characters" in str(e)

    # Test valid case
    result = _format_uuid("123456781234123412341234567890ab")
    assert result == "12345678-1234-1234-1234-1234567890ab"


def test_extract_block_id_exception_handling():
    """Test extract_block_id exception handling."""
    # Test with malformed URL that causes exception in parsing
    malformed_url = "https://notion.so/Page#[invalid-fragment]"
    result = extract_block_id(malformed_url)
    # Should fall back to general extraction and return None
    assert result is None


def test_extract_block_id_with_formatted_uuid_fragment():
    url = "https://www.notion.so/Page#12345678-1234-1234-1234-123456789abc"
    expected = "12345678-1234-1234-1234-123456789abc"
    assert extract_block_id(url) == expected


def test_extract_notion_id_empty_path():
    url = "https://notion.so/?p=abc123def456789012345678901234ab"
    expected = "abc123de-f456-7890-1234-5678901234ab"
    assert extract_notion_id(url) == expected


def test_extract_notion_id_empty_query_params():
    url = "https://notion.so/Page?p=&id="
    assert extract_notion_id(url) is None


def test_extract_notion_id_invalid_uuid_length_in_query():
    url = "https://notion.so/Page?p=tooshort"
    assert extract_notion_id(url) is None


def test_extract_notion_id_non_string_input():
    inputs = [123, [], {}, set()]
    for invalid_input in inputs:
        assert extract_notion_id(invalid_input) is None


def test_extract_notion_id_fragment_without_compact_match():
    url = "https://www.notion.so/Page#not-a-valid-uuid-fragment"
    assert extract_notion_id(url) is None


def test_extract_block_id_non_url_fallback():
    # This should fall back to extract_notion_id
    compact_uuid = "123456781234123412341234567890ab"
    expected = "12345678-1234-1234-1234-1234567890ab"
    assert extract_block_id(compact_uuid) == expected


def test_extract_block_id_url_without_protocol():
    result = extract_block_id("not-a-url-string")
    assert extract_notion_id("not-a-url-string") == result


def test_extract_notion_id_with_block_prefix_in_fragment():
    """Test fragment with 'block-' prefix in extract_notion_id (line 209)."""
    url = "https://www.notion.so/Page#block-abc123def456789012345678901234ab"
    expected = "abc123de-f456-7890-1234-5678901234ab"
    assert extract_notion_id(url) == expected


def test_extract_block_id_with_non_string_input():
    assert extract_block_id(None) is None
    assert extract_block_id(123) is None
    assert extract_block_id([]) is None


def test_extract_notion_id_url_parsing_exception():
    """Test exception handling in extract_notion_id URL parsing (lines 215-216)."""
    # Create a scenario that causes urlparse to fail
    # Using a very long string that might cause issues
    malformed_url = "https://" + "x" * 10000 + ".notion.so/test"
    result = extract_notion_id(malformed_url)
    # Should handle exception gracefully and return None
    assert result is None


def test_extract_block_id_url_parsing_exception():
    """Test exception handling in extract_block_id URL parsing."""
    # Use monkey patching to force the exception path specifically in extract_block_id
    import notion_client.helpers as helpers_module

    # Store original function
    original_urlparse = helpers_module.urlparse

    def mock_urlparse_exception(url):
        # Force an exception when parsing URLs in extract_block_id
        if "force-block-exception" in url:
            raise Exception(
                "Forced exception to test extract_block_id exception handling"
            )
        return original_urlparse(url)

    try:
        # Patch urlparse to throw exception during block ID URL parsing
        helpers_module.urlparse = mock_urlparse_exception

        # This should trigger the exception path in extract_block_id (lines 284-285)
        # The URL contains "://" so it enters the URL parsing path, then fails
        result = extract_block_id("https://notion.so/force-block-exception-test")
        assert (
            result is None
        ), "Should return None when exception occurs in extract_block_id"

    finally:
        # Restore original function
        helpers_module.urlparse = original_urlparse


@pytest.mark.vcr()
def test_iterate_data_source_templates(client, data_source_id):
    generator = iterate_data_source_templates(
        client.data_sources.list_templates,
        data_source_id=data_source_id,
    )
    assert isinstance(generator, GeneratorType)
    templates = [template for template in generator]
    assert isinstance(templates, list)


@pytest.mark.vcr()
def test_collect_data_source_templates(client, data_source_id):
    templates = collect_data_source_templates(
        client.data_sources.list_templates,
        data_source_id=data_source_id,
    )

    assert isinstance(templates, list)


@pytest.mark.vcr()
async def test_async_iterate_data_source_templates(
    async_client, async_test_data_source
):
    data_source_id = async_test_data_source

    generator = async_iterate_data_source_templates(
        async_client.data_sources.list_templates,
        data_source_id=data_source_id,
    )
    assert isinstance(generator, AsyncGeneratorType)
    templates = [template async for template in generator]
    assert isinstance(templates, list)


@pytest.mark.vcr()
async def test_async_collect_data_source_templates(
    async_client, async_test_data_source
):
    data_source_id = async_test_data_source

    templates = await async_collect_data_source_templates(
        async_client.data_sources.list_templates,
        data_source_id=data_source_id,
    )

    assert isinstance(templates, list)


def _create_rows(client, data_source_id, count=3):
    """Create rows in the data source and return them as a {name: id} dict."""
    return {
        f"row {i}": client.pages.create(
            parent={"data_source_id": data_source_id},
            properties={"Name": {"title": [{"text": {"content": f"row {i}"}}]}},
        )["id"]
        for i in range(count)
    }


async def _async_create_rows(client, data_source_id, count=3):
    """Create rows in the data source and return them as a {name: id} dict."""
    rows = {}
    for i in range(count):
        response = await client.pages.create(
            parent={"data_source_id": data_source_id},
            properties={"Name": {"title": [{"text": {"content": f"row {i}"}}]}},
        )
        rows[f"row {i}"] = response["id"]
    return rows


@pytest.mark.vcr()
def test_iterate_all_data_source_rows(client, data_source_id):
    rows_by_name = _create_rows(client, data_source_id)

    generator = iterate_all_data_source_rows(client, data_source_id=data_source_id)
    assert isinstance(generator, GeneratorType)

    assert {row["id"] for row in generator} == set(rows_by_name.values())


@pytest.mark.vcr()
def test_collect_all_data_source_rows(client, data_source_id):
    rows_by_name = _create_rows(client, data_source_id)

    rows = collect_all_data_source_rows(client, data_source_id=data_source_id)
    assert {row["id"] for row in rows} == set(rows_by_name.values())

    # A caller filter reaches the API alongside the created_time sort the
    # helper adds. Combining it with a window bound needs a data source past
    # the per-query result limit, which the mock-based tests cover instead.
    filtered = collect_all_data_source_rows(
        client,
        data_source_id=data_source_id,
        filter={"property": "Name", "title": {"equals": "row 1"}},
    )
    assert [row["id"] for row in filtered] == [rows_by_name["row 1"]]


@pytest.mark.vcr()
async def test_async_iterate_all_data_source_rows(async_client, async_test_data_source):
    data_source_id = async_test_data_source
    rows_by_name = await _async_create_rows(async_client, data_source_id)

    generator = async_iterate_all_data_source_rows(
        async_client, data_source_id=data_source_id
    )
    assert isinstance(generator, AsyncGeneratorType)

    ids = {row["id"] async for row in generator}
    assert ids == set(rows_by_name.values())


@pytest.mark.vcr()
async def test_async_collect_all_data_source_rows(async_client, async_test_data_source):
    data_source_id = async_test_data_source
    rows_by_name = await _async_create_rows(async_client, data_source_id)

    rows = await async_collect_all_data_source_rows(
        async_client, data_source_id=data_source_id
    )
    assert {row["id"] for row in rows} == set(rows_by_name.values())

    filtered = await async_collect_all_data_source_rows(
        async_client,
        data_source_id=data_source_id,
        filter={"property": "Name", "title": {"equals": "row 1"}},
    )
    assert [row["id"] for row in filtered] == [rows_by_name["row 1"]]


def _page(row_id, created_time):
    return {
        "object": "page",
        "id": row_id,
        "url": f"https://notion.so/{row_id}",
        "created_time": created_time,
    }


def _data_source_row(row_id, created_time):
    return {
        "object": "data_source",
        "id": row_id,
        "created_time": created_time,
    }


def _query_response(results, next_cursor=None, incomplete=False):
    body = {
        "object": "list",
        "type": "page_or_data_source",
        "page_or_data_source": {},
        "results": results,
        "has_more": next_cursor is not None,
        "next_cursor": next_cursor,
    }
    if incomplete:
        body["request_status"] = {
            "type": "incomplete",
            "incomplete_reason": "query_result_limit_reached",
        }
    return body


def _make_client(query_side_effect, async_query=False):
    query = AsyncMock() if async_query else MagicMock()
    query.side_effect = query_side_effect
    client = MagicMock()
    client.data_sources.query = query
    return client, query


def test_iterate_all_data_source_rows_single_complete_window():
    client, query = _make_client(
        [
            _query_response(
                [
                    _page("r1", "2024-01-01T00:00:00.000Z"),
                    _page("r2", "2024-01-02T00:00:00.000Z"),
                ]
            )
        ]
    )

    ids = [
        row["id"] for row in iterate_all_data_source_rows(client, data_source_id="ds-1")
    ]

    assert ids == ["r1", "r2"]
    assert query.call_count == 1
    call = query.call_args
    assert call.kwargs["sorts"] == [
        {"timestamp": "created_time", "direction": "ascending"}
    ]
    assert "filter" not in call.kwargs
    assert call.kwargs["start_cursor"] is None


def test_iterate_all_data_source_rows_advances_past_limit_and_dedupes():
    # Window 1: two pages, then the second call hits the limit (incomplete).
    # Window 2: starts at the last created_time, re-sees r4, then finishes.
    client, query = _make_client(
        [
            _query_response(
                [
                    _page("r1", "2024-01-01T00:00:00.000Z"),
                    _page("r2", "2024-01-02T00:00:00.000Z"),
                ],
                next_cursor="c1",
            ),
            _query_response(
                [
                    _page("r3", "2024-01-03T00:00:00.000Z"),
                    _page("r4", "2024-01-04T00:00:00.000Z"),
                ],
                incomplete=True,
            ),
            _query_response(
                [
                    _page("r4", "2024-01-04T00:00:00.000Z"),
                    _page("r5", "2024-01-05T00:00:00.000Z"),
                ]
            ),
        ]
    )

    ids = [
        row["id"] for row in iterate_all_data_source_rows(client, data_source_id="ds-1")
    ]

    assert ids == ["r1", "r2", "r3", "r4", "r5"]
    assert query.call_count == 3
    # Inner pagination carried the cursor within window 1.
    assert query.call_args_list[1].kwargs["start_cursor"] == "c1"
    # Window 2 reset the cursor and added the created_time lower bound.
    assert query.call_args_list[2].kwargs["start_cursor"] is None
    assert query.call_args_list[2].kwargs["filter"] == {
        "timestamp": "created_time",
        "created_time": {"on_or_after": "2024-01-04T00:00:00.000Z"},
    }


def test_iterate_all_data_source_rows_combines_caller_filter_with_and():
    caller_filter = {"property": "Status", "status": {"equals": "Done"}}
    client, query = _make_client(
        [
            _query_response([_page("r1", "2024-01-01T00:00:00.000Z")], incomplete=True),
            _query_response(
                [
                    _page("r1", "2024-01-01T00:00:00.000Z"),
                    _page("r2", "2024-02-01T00:00:00.000Z"),
                ]
            ),
        ]
    )

    ids = [
        row["id"]
        for row in iterate_all_data_source_rows(
            client, data_source_id="ds-1", filter=caller_filter
        )
    ]

    assert ids == ["r1", "r2"]
    # First window: caller filter only.
    assert query.call_args_list[0].kwargs["filter"] == caller_filter
    # Second window: caller filter AND created_time bound.
    assert query.call_args_list[1].kwargs["filter"] == {
        "and": [
            caller_filter,
            {
                "timestamp": "created_time",
                "created_time": {"on_or_after": "2024-01-01T00:00:00.000Z"},
            },
        ]
    }


def test_iterate_all_data_source_rows_advances_on_data_source_boundary():
    # Window 1 ends at the limit on a child data-source row (wiki data source).
    # The window must advance from that row's created_time, even though it is
    # not a page.
    client, query = _make_client(
        [
            _query_response(
                [
                    _page("r1", "2024-01-01T00:00:00.000Z"),
                    _data_source_row("ds-child", "2024-01-02T00:00:00.000Z"),
                ],
                incomplete=True,
            ),
            _query_response(
                [
                    _data_source_row("ds-child", "2024-01-02T00:00:00.000Z"),
                    _page("r2", "2024-01-03T00:00:00.000Z"),
                ]
            ),
        ]
    )

    ids = [
        row["id"] for row in iterate_all_data_source_rows(client, data_source_id="ds-1")
    ]

    assert ids == ["r1", "ds-child", "r2"]
    assert query.call_count == 2
    # The second window advanced from the data-source row's created_time.
    assert query.call_args_list[1].kwargs["filter"] == {
        "timestamp": "created_time",
        "created_time": {"on_or_after": "2024-01-02T00:00:00.000Z"},
    }


def test_iterate_all_data_source_rows_ignores_partial_rows_as_boundary():
    # A partial row carries no created_time to bound the next window with, so
    # the window advances from the last full row instead. It is still yielded.
    partial = {"object": "page", "id": "r2"}
    client, query = _make_client(
        [
            _query_response(
                [_page("r1", "2024-01-01T00:00:00.000Z"), partial], incomplete=True
            ),
            _query_response([_page("r3", "2024-01-02T00:00:00.000Z")]),
        ]
    )

    ids = [
        row["id"] for row in iterate_all_data_source_rows(client, data_source_id="ds-1")
    ]

    assert ids == ["r1", "r2", "r3"]
    assert query.call_args_list[1].kwargs["filter"] == {
        "timestamp": "created_time",
        "created_time": {"on_or_after": "2024-01-01T00:00:00.000Z"},
    }


def test_iterate_all_data_source_rows_throws_when_one_created_time_exceeds_limit():
    same_time = "2024-01-01T00:00:00.000Z"
    client, _ = _make_client(
        [
            _query_response(
                [_page("r1", same_time), _page("r2", same_time)], incomplete=True
            ),
            _query_response(
                [_page("r1", same_time), _page("r2", same_time)], incomplete=True
            ),
        ]
    )

    with pytest.raises(RuntimeError, match="Cannot make progress"):
        collect_all_data_source_rows(client, data_source_id="ds-1")


def test_iterate_all_data_source_rows_merges_into_caller_and_filter():
    # A top-level `and` is extended in place rather than nested, so the bound
    # stays within Notion's two-level filter nesting limit.
    done = {"property": "Status", "status": {"equals": "Done"}}
    urgent = {"property": "Priority", "select": {"equals": "Urgent"}}
    client, query = _make_client(
        [
            _query_response([_page("r1", "2024-01-01T00:00:00.000Z")], incomplete=True),
            _query_response([_page("r1", "2024-01-01T00:00:00.000Z")]),
        ]
    )

    collect_all_data_source_rows(
        client, data_source_id="ds-1", filter={"and": [done, urgent]}
    )

    assert query.call_args_list[1].kwargs["filter"] == {
        "and": [
            done,
            urgent,
            {
                "timestamp": "created_time",
                "created_time": {"on_or_after": "2024-01-01T00:00:00.000Z"},
            },
        ]
    }


def test_iterate_all_data_source_rows_keeps_or_nested_in_and():
    # A top-level `or` is rejected, but the documented workaround of wrapping it
    # in an `and` must survive: the bound joins the outer `and` and the `or`
    # passes through untouched.
    or_group = {
        "or": [
            {"property": "Status", "status": {"equals": "Done"}},
            {"property": "Status", "status": {"equals": "In progress"}},
        ]
    }
    client, query = _make_client(
        [
            _query_response([_page("r1", "2024-01-01T00:00:00.000Z")], incomplete=True),
            _query_response([_page("r1", "2024-01-01T00:00:00.000Z")]),
        ]
    )

    collect_all_data_source_rows(
        client, data_source_id="ds-1", filter={"and": [or_group]}
    )

    assert query.call_args_list[1].kwargs["filter"] == {
        "and": [
            or_group,
            {
                "timestamp": "created_time",
                "created_time": {"on_or_after": "2024-01-01T00:00:00.000Z"},
            },
        ]
    }


@pytest.mark.parametrize("managed_kwarg", ["start_cursor", "sorts"])
def test_iterate_all_data_source_rows_rejects_managed_kwargs(managed_kwarg):
    client, query = _make_client([_query_response([])])

    with pytest.raises(TypeError, match=f"`{managed_kwarg}` is not accepted here"):
        collect_all_data_source_rows(
            client, data_source_id="ds-1", **{managed_kwarg: "whatever"}
        )
    query.assert_not_called()


def test_iterate_all_data_source_rows_validates_before_iterating():
    # Arguments are checked when the helper is called, not on first iteration,
    # so a caller who never iterates still hears about them.
    client, _ = _make_client([_query_response([])])

    with pytest.raises(TypeError, match="`sorts` is not accepted here"):
        iterate_all_data_source_rows(client, data_source_id="ds-1", sorts=[])

    with pytest.raises(ValueError, match="top-level `or` filter"):
        iterate_all_data_source_rows(
            client, data_source_id="ds-1", filter={"or": [{"property": "Name"}]}
        )


def test_async_iterate_all_data_source_rows_validates_before_iterating():
    client, _ = _make_client([_query_response([])], async_query=True)

    with pytest.raises(TypeError, match="`start_cursor` is not accepted here"):
        async_iterate_all_data_source_rows(
            client, data_source_id="ds-1", start_cursor="c1"
        )


def test_iterate_all_data_source_rows_rejects_top_level_or_filter():
    client, query = _make_client([_query_response([])])
    or_filter = {
        "or": [
            {"property": "Status", "status": {"equals": "Done"}},
            {"property": "Status", "status": {"equals": "In progress"}},
        ]
    }

    with pytest.raises(ValueError, match="top-level `or` filter"):
        collect_all_data_source_rows(client, data_source_id="ds-1", filter=or_filter)
    query.assert_not_called()


def test_collect_all_data_source_rows_across_windows():
    client, query = _make_client(
        [
            _query_response([_page("r1", "2024-01-01T00:00:00.000Z")], incomplete=True),
            _query_response(
                [
                    _page("r1", "2024-01-01T00:00:00.000Z"),
                    _page("r2", "2024-01-02T00:00:00.000Z"),
                ]
            ),
        ]
    )

    rows = collect_all_data_source_rows(client, data_source_id="ds-1")

    assert [r["id"] for r in rows] == ["r1", "r2"]
    assert query.call_count == 2


async def test_async_iterate_all_data_source_rows_advances_past_limit():
    client, _ = _make_client(
        [
            _query_response([_page("r1", "2024-01-01T00:00:00.000Z")], incomplete=True),
            _query_response(
                [
                    _page("r1", "2024-01-01T00:00:00.000Z"),
                    _page("r2", "2024-01-02T00:00:00.000Z"),
                ]
            ),
        ],
        async_query=True,
    )

    ids = []
    async for row in async_iterate_all_data_source_rows(client, data_source_id="ds-1"):
        ids.append(row["id"])

    assert ids == ["r1", "r2"]


async def test_async_iterate_all_data_source_rows_throws_when_window_cannot_advance():
    same_time = "2024-01-01T00:00:00.000Z"
    client, _ = _make_client(
        [
            _query_response([_page("r1", same_time)], incomplete=True),
            _query_response([_page("r1", same_time)], incomplete=True),
        ],
        async_query=True,
    )

    with pytest.raises(RuntimeError, match="Cannot make progress"):
        await async_collect_all_data_source_rows(client, data_source_id="ds-1")


async def test_async_collect_all_data_source_rows_single_window():
    client, _ = _make_client(
        [
            _query_response(
                [
                    _page("r1", "2024-01-01T00:00:00.000Z"),
                    _page("r2", "2024-01-02T00:00:00.000Z"),
                ]
            )
        ],
        async_query=True,
    )

    rows = await async_collect_all_data_source_rows(client, data_source_id="ds-1")

    assert [r["id"] for r in rows] == ["r1", "r2"]
