import asyncio
import time
from types import AsyncGeneratorType, GeneratorType

import pytest

from notion_client.helpers import (
    async_collect_paginated_api,
    async_iterate_paginated_api,
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
    is_full_page,
    is_full_page_or_database,
    is_full_user,
    is_mention_rich_text_item_response,
    is_text_rich_text_item_response,
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
@pytest.mark.timeout(90)
def test_iterate_paginated_api(client, parent_page_id):
    def create_page(page_name):
        page = client.pages.create(
            parent={"page_id": parent_page_id},
            properties={"title": [{"text": {"content": page_name}}]},
            children=[],
        )
        return page["id"]

    page_ids = []
    for i in range(0, 5):
        page_id = create_page(f"Test Page (test_iterate_paginated_api iteration {i})")
        page_ids.append(page_id)

    # give time to Notion to index these pages
    time.sleep(20)

    generator = iterate_paginated_api(
        client.search,
        query="test_iterate_paginated_api",
        page_size=2,
    )
    assert isinstance(generator, GeneratorType)
    results = [result for result in generator]
    assert len(results) == 5

    for page_id in page_ids:
        client.blocks.delete(block_id=page_id)

    time.sleep(20)

    generator = iterate_paginated_api(
        client.search,
        query="test_iterate_paginated_api",
        page_size=2,
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
@pytest.mark.timeout(90)
async def test_async_iterate_paginated_api(async_client, parent_page_id):
    async def create_page(page_name):
        page = await async_client.pages.create(
            parent={"page_id": parent_page_id},
            properties={"title": [{"text": {"content": page_name}}]},
            children=[],
        )
        return page["id"]

    page_ids = []
    for i in range(0, 5):
        page_id = await create_page(
            f"Test Page (test_async_iterate_paginated_api iteration {i})"
        )
        page_ids.append(page_id)

    # give time to Notion to index these pages
    await asyncio.sleep(20)

    generator = async_iterate_paginated_api(
        async_client.search,
        query="test_async_iterate_paginated_api",
        page_size=2,
    )
    assert isinstance(generator, AsyncGeneratorType)
    results = [result async for result in generator]
    assert len(results) == 5

    for page_id in page_ids:
        await async_client.blocks.delete(block_id=page_id)

    await asyncio.sleep(20)

    generator = async_iterate_paginated_api(
        async_client.search,
        query="test_async_iterate_paginated_api",
        page_size=2,
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
def test_is_full_database(client, database_id):
    response = client.databases.retrieve(database_id=database_id)
    assert is_full_database(response)


@pytest.mark.vcr()
def test_is_full_page_or_database(client, database_id, page_id):
    response = client.pages.retrieve(page_id=page_id)
    assert is_full_page_or_database(response)

    response = client.databases.retrieve(database_id=database_id)
    assert is_full_page_or_database(response)


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


class TestIdExtractionUtilities:
    """Test the ID extraction utilities."""
    
    def test_extract_notion_id_with_standard_urls(self):
        """Test extracting ID from standard Notion URLs."""
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
    
    def test_extract_notion_id_prioritizes_path_over_query(self):
        """Test that path ID is prioritized over query parameters."""
        # This is the key fix - database ID in path should be extracted, not view ID in query
        url = "https://notion.so/workspace/MyDB-abc123def456789012345678901234ab?v=def456789012345678901234abcdef12"
        result = extract_notion_id(url)
        assert result == "abc123de-f456-7890-1234-5678901234ab"  # DB ID, not view ID
    
    def test_extract_notion_id_uses_query_when_no_path_id(self):
        """Test using query parameters when no path ID is available."""
        url = "https://notion.so/share?p=abc123def456789012345678901234ab"
        result = extract_notion_id(url)
        assert result == "abc123de-f456-7890-1234-5678901234ab"
    
    def test_extract_notion_id_handles_formatted_uuids(self):
        """Test handling already formatted UUIDs."""
        uuid = "12345678-1234-1234-1234-123456789abc"
        assert extract_notion_id(uuid) == "12345678-1234-1234-1234-123456789abc"
    
    def test_extract_notion_id_formats_compact_uuids(self):
        """Test formatting compact UUIDs."""
        compact_uuid = "123456781234123412341234567890ab"
        assert extract_notion_id(compact_uuid) == "12345678-1234-1234-1234-1234567890ab"
    
    def test_extract_notion_id_returns_none_for_invalid_inputs(self):
        """Test returning None for invalid inputs."""
        invalid_inputs = ["", "not-a-url", "12345", None]
        for invalid_input in invalid_inputs:
            assert extract_notion_id(invalid_input) is None
    
    def test_extract_notion_id_handles_different_domains(self):
        """Test handling different valid Notion domains."""
        test_id = "abc123def456789012345678901234ab"
        expected = "abc123de-f456-7890-1234-5678901234ab"
        
        domains = [
            "https://notion.so/Page-" + test_id,
            "https://www.notion.so/Page-" + test_id,
            "https://notion.site/Page-" + test_id,
        ]
        
        for url in domains:
            assert extract_notion_id(url) == expected
    
    def test_extract_notion_id_rejects_invalid_domains(self):
        """Test rejecting invalid domains."""
        invalid_urls = [
            "https://google.com/123456781234123412341234567890ab",
            "https://example.com/Page-abc123def456789012345678901234ab",
        ]
        
        for url in invalid_urls:
            assert extract_notion_id(url) is None
    
    def test_extract_database_id(self):
        """Test database ID extraction."""
        url = "https://www.notion.so/Tasks-abc123def456789012345678901234ab"
        assert extract_database_id(url) == "abc123de-f456-7890-1234-5678901234ab"
    
    def test_extract_page_id(self):
        """Test page ID extraction."""
        url = "https://www.notion.so/My-Page-123456781234123412341234567890ab"
        assert extract_page_id(url) == "12345678-1234-1234-1234-1234567890ab"
    
    def test_extract_block_id_from_fragment(self):
        """Test extracting block ID from URL fragment."""
        url = "https://www.notion.so/Page#block-def456789012345678901234abcdef12"
        assert extract_block_id(url) == "def45678-9012-3456-7890-1234abcdef12"
    
    def test_extract_block_id_without_block_prefix(self):
        """Test extracting block ID without block- prefix."""
        url = "https://www.notion.so/Page#def456789012345678901234abcdef12"
        assert extract_block_id(url) == "def45678-9012-3456-7890-1234abcdef12"
    
    def test_extract_block_id_returns_none_without_fragment(self):
        """Test returning None if no block fragment."""
        assert extract_block_id("https://www.notion.so/Page") is None
    
    def test_extract_block_id_fallback_to_general(self):
        """Test fallback to general ID extraction for non-URL inputs."""
        uuid = "12345678-1234-1234-1234-123456789abc"
        assert extract_block_id(uuid) == "12345678-1234-1234-1234-123456789abc"
    
    def test_extract_notion_id_case_insensitive(self):
        """Test that extraction is case insensitive."""
        test_cases = [
            "ABC123DEF456789012345678901234AB",
            "abc123def456789012345678901234ab",
            "AbC123dEf456789012345678901234Ab",
        ]
        expected = "abc123de-f456-7890-1234-5678901234ab"
        
        for test_id in test_cases:
            assert extract_notion_id(test_id) == expected
    
    def test_extract_notion_id_with_mixed_case_uuid(self):
        """Test handling mixed case formatted UUIDs."""
        mixed_case_uuid = "12345678-1234-1234-1234-123456789ABC"
        expected = "12345678-1234-1234-1234-123456789abc"
        assert extract_notion_id(mixed_case_uuid) == expected
    
    def test_extract_notion_id_with_whitespace(self):
        """Test trimming whitespace from inputs."""
        uuid_with_whitespace = "  12345678-1234-1234-1234-123456789abc  "
        expected = "12345678-1234-1234-1234-123456789abc"
        assert extract_notion_id(uuid_with_whitespace) == expected
    
    def test_extract_notion_id_with_query_id_param(self):
        """Test extracting from 'id' query parameter."""
        url = "https://notion.so/share?id=abc123def456789012345678901234ab"
        expected = "abc123de-f456-7890-1234-5678901234ab"
        assert extract_notion_id(url) == expected
