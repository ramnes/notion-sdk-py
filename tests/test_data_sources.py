"""Tests for DataSourcesEndpoint functionality (2025-09-03 API)."""

import pytest


@pytest.mark.vcr()
def test_data_sources_retrieve(client, data_source_id):
    """Test retrieving a data source by ID."""
    response = client.data_sources.retrieve(data_source_id=data_source_id)

    assert response["object"] == "data_source"
    assert response["id"] == data_source_id
    assert "properties" in response
    assert "title" in response


@pytest.mark.vcr()
def test_data_sources_query(client, data_source_id):
    """Test querying a data source with various filters."""
    # Basic query
    response = client.data_sources.query(data_source_id=data_source_id)

    assert response["object"] == "list"
    assert "results" in response
    assert response["data_source_id"] == data_source_id

    # Query with pagination
    response_paginated = client.data_sources.query(
        data_source_id=data_source_id, page_size=5, start_cursor=None
    )

    assert response_paginated["object"] == "list"
    assert len(response_paginated["results"]) <= 5


@pytest.mark.vcr()
def test_data_sources_query_with_filter(client, data_source_id):
    """Test querying a data source with filters."""
    response = client.data_sources.query(
        data_source_id=data_source_id,
        filter={"property": "Status", "select": {"equals": "Done"}},
    )

    assert response["object"] == "list"
    assert response["data_source_id"] == data_source_id


@pytest.mark.vcr()
def test_data_sources_query_with_sorts(client, data_source_id):
    """Test querying a data source with sorting."""
    response = client.data_sources.query(
        data_source_id=data_source_id,
        sorts=[{"property": "Created", "direction": "descending"}],
    )

    assert response["object"] == "list"
    assert response["data_source_id"] == data_source_id


@pytest.mark.vcr()
def test_data_sources_update(client, data_source_id):
    """Test updating a data source properties and title."""
    # Update title
    response = client.data_sources.update(
        data_source_id=data_source_id,
        title=[{"text": {"content": "Updated Data Source Title"}}],
    )

    assert response["object"] == "data_source"
    assert response["id"] == data_source_id

    # Update properties schema
    response = client.data_sources.update(
        data_source_id=data_source_id,
        properties={"Test Property": {"type": "rich_text", "rich_text": {}}},
    )

    assert response["object"] == "data_source"
    assert "Test Property" in response["properties"]


@pytest.mark.vcr()
def test_data_sources_update_in_trash(client, data_source_id):
    """Test moving a data source to trash and restoring."""
    # Move to trash
    response = client.data_sources.update(data_source_id=data_source_id, in_trash=True)

    assert response["object"] == "data_source"
    assert response["in_trash"] is True

    # Restore from trash
    response = client.data_sources.update(data_source_id=data_source_id, in_trash=False)

    assert response["object"] == "data_source"
    assert response["in_trash"] is False


@pytest.mark.vcr()
async def test_async_data_sources_retrieve(async_client, data_source_id):
    """Test async data source retrieval."""
    response = await async_client.data_sources.retrieve(data_source_id=data_source_id)

    assert response["object"] == "data_source"
    assert response["id"] == data_source_id


@pytest.mark.vcr()
async def test_async_data_sources_query(async_client, data_source_id):
    """Test async data source querying."""
    response = await async_client.data_sources.query(data_source_id=data_source_id)

    assert response["object"] == "list"
    assert response["data_source_id"] == data_source_id


@pytest.mark.vcr()
async def test_async_data_sources_update(async_client, data_source_id):
    """Test async data source updating."""
    response = await async_client.data_sources.update(
        data_source_id=data_source_id,
        title=[{"text": {"content": "Async Updated Title"}}],
    )

    assert response["object"] == "data_source"
    assert response["id"] == data_source_id


def test_data_sources_query_parameter_filtering(client):
    """Test that query parameters are properly filtered."""
    from notion_client.helpers import pick

    # Test parameter filtering for query method
    test_kwargs = {
        "data_source_id": "test-id",
        "filter": {"property": "test"},
        "sorts": [{"property": "test", "direction": "ascending"}],
        "start_cursor": "test-cursor",
        "page_size": 50,
        "archived": True,
        "in_trash": False,
        "extra_param": "should_be_filtered_out",
        "auth": "test-auth",
    }

    # Test query parameters
    pick(test_kwargs, "filter_properties")
    body_params = pick(
        test_kwargs,
        "filter",
        "sorts",
        "start_cursor",
        "page_size",
        "archived",
        "in_trash",
    )

    assert "extra_param" not in body_params
    assert "auth" not in body_params
    assert "filter" in body_params
    assert "sorts" in body_params


def test_data_sources_update_parameter_filtering(client):
    """Test that update parameters are properly filtered."""
    from notion_client.helpers import pick

    test_kwargs = {
        "data_source_id": "test-id",
        "properties": {"test": {"type": "title"}},
        "title": [{"text": {"content": "test"}}],
        "in_trash": False,
        "extra_param": "should_be_filtered_out",
        "auth": "test-auth",
    }

    body_params = pick(test_kwargs, "properties", "title", "in_trash")

    assert "extra_param" not in body_params
    assert "auth" not in body_params
    assert "properties" in body_params
    assert "title" in body_params


def test_data_sources_create_builds_correct_request_body():
    """Unit test: data_sources.create builds proper payload and path."""
    from unittest.mock import MagicMock
    from notion_client import Client

    client = Client(auth="test-token", notion_version="2025-09-03")
    client.request = MagicMock(return_value={"object": "data_source"})

    parent = {"type": "database_id", "database_id": "db-123"}
    props = {"Name": {"title": {}}, "In stock": {"checkbox": {}}}
    title = [{"text": {"content": "Retail Inventory"}}]

    res = client.data_sources.create(parent=parent, properties=props, title=title)

    assert res["object"] == "data_source"
    client.request.assert_called_once()
    call = client.request.call_args
    assert call.kwargs["path"] == "data_sources"
    assert call.kwargs["method"] == "POST"
    body = call.kwargs["body"]
    assert body["parent"] == parent
    assert body["properties"] == props
    assert body["title"] == title


def test_data_sources_create_parameter_filtering():
    """Unit test: extra params are filtered out by create."""
    from unittest.mock import MagicMock
    from notion_client import Client

    client = Client(auth="test-token", notion_version="2025-09-03")
    client.request = MagicMock(return_value={"object": "data_source"})

    client.data_sources.create(
        parent={"type": "database_id", "database_id": "db-123"},
        properties={"Name": {"title": {}}},
        title=[{"text": {"content": "X"}}],
        extra_param="ignore-me",
        auth="override-auth",
    )

    call = client.request.call_args
    body = call.kwargs["body"]
    assert "extra_param" not in body
    assert "auth" not in body
