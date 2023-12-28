import asyncio
import time
from types import AsyncGeneratorType, GeneratorType

import pytest

from notion_client.helpers import (
    async_collect_paginated_api,
    async_iterate_paginated_api,
    collect_paginated_api,
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
