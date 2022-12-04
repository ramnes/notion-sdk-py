from types import AsyncGeneratorType, GeneratorType

import pytest

from notion_client.helpers import (
    async_collect_paginated_api,
    async_iterate_paginated_api,
    collect_paginated_api,
    get_id,
    get_url,
    is_full_block,
    is_full_comment,
    is_full_database,
    is_full_page,
    is_full_user,
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
    assert pick(my_dict, "optional-variable") == {}


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
        get_id("https://notion.so/123")
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
def test_iterate_paginated_api(client):
    function = client.search
    generator = iterate_paginated_api(function)

    assert type(generator) == GeneratorType
    assert next(generator) is not None

    generator_empty = iterate_paginated_api(
        function, query="This should have no results"
    )
    assert next(generator_empty) == []


@pytest.mark.vcr()
def test_collect_paginated_api(client):
    function = client.search
    results = collect_paginated_api(function)

    assert type(results) == list
    assert results != []

    results_empty = collect_paginated_api(function, query="This should have no results")
    assert results_empty == []


@pytest.mark.vcr()
async def test_async_iterate_paginated_api(async_client):
    function = async_client.search
    generator = async_iterate_paginated_api(function)

    assert type(generator) == AsyncGeneratorType
    assert await generator.__anext__() is not None

    generator_empty = async_iterate_paginated_api(
        function, query="This should have no results"
    )
    assert await generator_empty.__anext__() == []


@pytest.mark.vcr()
async def test_async_collect_paginated_api(async_client):
    function = async_client.search
    results = await async_collect_paginated_api(function)

    assert type(results) == list
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
def test_is_full_user(client):
    response = client.users.me()
    assert is_full_user(response)


@pytest.mark.vcr()
def test_is_full_comment(client, page_id, comment_id):
    response = client.comments.list(block_id=page_id)
    assert is_full_comment(response)
