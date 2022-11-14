from datetime import datetime

import pytest

from tests.conftest import TEST_PAGE_NAME


@pytest.mark.vcr()
def test_pages_create(client, page_id):
    response = client.pages.create(
        parent={"page_id": page_id},
        properties={
            "title": [{"text": {"content": TEST_PAGE_NAME}}],
        },
        children=[],
    )

    assert response["object"] == "page"


@pytest.mark.vcr()
def test_pages_retrieve(client, session_page_id):
    response = client.pages.retrieve(page_id=session_page_id)
    assert response["object"] == "page"


@pytest.mark.vcr()
def test_pages_update(client, session_page_id):
    icon = {"type": "emoji", "emoji": "🛴"}

    response = client.pages.update(page_id=session_page_id, icon=icon)
    assert response["icon"]


@pytest.mark.vcr()
def test_pages_properties_retrieve(client, session_page_id):
    response = client.pages.properties.retrieve(
        page_id=session_page_id, property_id="title"
    )
    assert response["results"][0]["type"] == "title"


@pytest.mark.vcr()
def test_blocks_children_create(client, session_page_id) -> str:
    children = [
        {"paragraph": {"rich_text": [{"text": {"content": "I'm a paragraph."}}]}}
    ]

    response = client.blocks.children.append(
        block_id=session_page_id, children=children
    )

    assert response["object"] == "list"
    assert len(response["results"]) > 0
    assert response["results"][0]["id"]


@pytest.mark.vcr()
def test_blocks_children_list(client, session_page_id):
    response = client.blocks.children.list(block_id=session_page_id)
    assert response["object"] == "list"
    assert response["type"] == "block"


@pytest.mark.vcr()
def test_blocks_retrieve(client, session_block_id):
    response = client.blocks.retrieve(block_id=session_block_id)
    assert response["object"] == "block"
    assert response["type"] == "paragraph"


@pytest.mark.vcr()
def test_blocks_update(client, session_block_id):
    new_plain_text = "I'm an updated paragraph."
    new_text = {
        "rich_text": [
            {
                "text": {"content": new_plain_text},
                "annotations": {"bold": True, "color": "red_background"},
            }
        ]
    }
    response = client.blocks.update(block_id=session_block_id, paragraph=new_text)

    assert response["paragraph"]["rich_text"][0]["plain_text"]


@pytest.mark.vcr()
def test_blocks_delete(client, session_block_id):
    client.blocks.delete(block_id=session_block_id)

    new_retrieve = client.blocks.retrieve(block_id=session_block_id)
    assert new_retrieve["archived"]


@pytest.mark.vcr()
def test_users_list(client):
    response = client.users.list()
    assert response["type"] == "user"


@pytest.mark.vcr()
def test_users_me(client):
    response = client.users.me()
    assert response["type"] == "bot"
    assert response["id"]


@pytest.mark.vcr()
def test_users_retrieve(client):
    me = client.users.me()
    response = client.users.retrieve(me["id"])
    assert response == me


@pytest.mark.vcr()
def test_search(client, page_id):
    payload = {
        "query": page_id,
        "sort": {
            "direction": "descending",
            "timestamp": "last_edited_time",
        },
    }

    response = client.search(**payload)
    assert response["results"]


@pytest.mark.vcr()
def test_databases_create(client, session_page_id):
    db_name = f"Test Database - {datetime.now()}"
    properties = {
        "Name": {"title": {}},  # required property
    }
    title = [{"type": "text", "text": {"content": db_name}}]
    parent = {"type": "page_id", "page_id": session_page_id}
    response = client.databases.create(
        **{"parent": parent, "title": title, "properties": properties}
    )

    assert response["object"] == "database"


@pytest.mark.vcr()
def test_databases_query(client, session_database_id):
    query = {
        "database_id": session_database_id,
        "filter": {"timestamp": "created_time", "created_time": {"past_week": {}}},
    }

    response = client.databases.query(**query)
    assert response["object"] == "list"
    assert not response["results"]


@pytest.mark.vcr()
def test_databases_retrieve(client, session_database_id):

    response = client.databases.retrieve(session_database_id)
    assert response["object"] == "database"


@pytest.mark.vcr()
def test_databases_update(client, session_database_id):
    icon = {"type": "emoji", "emoji": "🔥"}

    response = client.databases.update(database_id=session_database_id, icon=icon)
    assert response["icon"]


@pytest.mark.vcr()
def test_comments_create(client, session_page_id):
    parent = {"page_id": session_page_id}
    rich_text = [
        {
            "text": {
                "content": "This is a test comment.",
            },
        },
    ]

    response = client.comments.create(parent=parent, rich_text=rich_text)
    assert response


@pytest.mark.vcr()
def test_comments_list(client, session_page_id):

    response = client.comments.list(block_id=session_page_id)

    assert response["object"] == "list"
    assert response["results"]
    assert response["results"][0]["object"] == "comment"


@pytest.mark.vcr()
def test_pages_delete(client, session_page_id) -> str:
    response = client.blocks.delete(block_id=session_page_id)
    assert response
