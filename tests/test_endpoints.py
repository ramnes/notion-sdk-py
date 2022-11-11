from datetime import datetime

import pytest

from tests.conftest import TEST_PAGE_NAME


@pytest.fixture(scope="session")
def session_page_id(client, page_id) -> str:
    response = client.pages.create(
        parent={"page_id": page_id},
        properties={
            "title": [{"text": {"content": TEST_PAGE_NAME}}],
        },
        children=[],
    )

    yield response["id"]
    client.blocks.delete(block_id=response["id"])


@pytest.fixture(scope="session")
def session_block_id(client, session_page_id) -> str:
    children = [
        {"paragraph": {"rich_text": [{"text": {"content": "I'm a paragraph."}}]}}
    ]

    response = client.blocks.children.append(
        block_id=session_page_id, children=children
    )

    return response["results"][0]["id"]


@pytest.fixture(scope="session")
def session_database_id(client, session_page_id) -> str:
    db_name = f"Test Database - {datetime.now()}"
    properties = {
        "Name": {"title": {}},  # required property
    }
    title = [{"type": "text", "text": {"content": db_name}}]
    parent = {"type": "page_id", "page_id": session_page_id}
    response = client.databases.create(
        **{"parent": parent, "title": title, "properties": properties}
    )

    return response["id"]


@pytest.fixture(scope="session")
def session_comment_id(client, session_page_id) -> str:
    parent = {"page_id": session_page_id}
    rich_text = [
        {
            "text": {
                "content": "This is a test comment.",
            },
        },
    ]

    response = client.comments.create(parent=parent, rich_text=rich_text)
    return response["id"]


def compare_cleaned_ids(id1: str, id2: str) -> bool:
    return id1.replace("-", "").strip() == id2.replace("-", "").strip()


def test_pages_retrieve(client, session_page_id, page_id):
    response = client.pages.retrieve(page_id=session_page_id)
    assert response["object"] == "page"
    assert compare_cleaned_ids(response["parent"]["page_id"], page_id)


def test_pages_update(client, session_page_id):
    icon = {"type": "emoji", "emoji": "🛴"}

    response = client.pages.update(page_id=session_page_id, icon=icon)
    assert response["icon"] == icon


def test_pages_properties_retrieve(client, session_page_id):
    response = client.pages.properties.retrieve(
        page_id=session_page_id, property_id="title"
    )
    assert response["results"][0]["type"] == "title"


def test_blocks_children_list(client, session_page_id, session_block_id):
    response = client.blocks.children.list(block_id=session_page_id)
    assert response["object"] == "list"
    assert response["type"] == "block"
    assert compare_cleaned_ids(response["results"][0]["id"], session_block_id)


def test_blocks_retrieve(client, session_block_id):
    response = client.blocks.retrieve(block_id=session_block_id)
    assert response["object"] == "block"
    assert response["type"] == "paragraph"
    assert compare_cleaned_ids(response["id"], session_block_id)


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

    assert compare_cleaned_ids(response["id"], session_block_id)
    assert response["paragraph"]["rich_text"][0]["plain_text"] == new_plain_text


def test_blocks_delete(client, session_block_id):
    response = client.blocks.delete(block_id=session_block_id)

    assert compare_cleaned_ids(response["id"], session_block_id)

    new_retrieve = client.blocks.retrieve(block_id=session_block_id)
    assert new_retrieve["archived"]


def test_users_list(client):
    response = client.users.list()
    assert response["type"] == "user"
    assert response["results"][0]["name"] == "Notion Testing Account"


def test_users_me(client):
    response = client.users.me()
    assert response["type"] == "bot"
    assert response["id"]


def test_users_retrieve(client):
    me = client.users.me()
    response = client.users.retrieve(me["id"])
    assert response == me


def test_search(client, page_id):
    payload = {
        "query": "Test",
        "sort": {
            "direction": "ascending",
            "timestamp": "last_edited_time",
        },
    }

    response = client.search(**payload)
    assert response["results"]
    assert compare_cleaned_ids(response["results"][0]["id"], page_id)


def test_databases_query(client, session_database_id):
    query = {
        "database_id": session_database_id,
        "filter": {"timestamp": "created_time", "created_time": {"past_week": {}}},
    }

    response = client.databases.query(**query)
    assert response["object"] == "list"
    assert not response["results"]


def test_databases_retrieve(client, session_database_id, session_page_id):

    response = client.databases.retrieve(session_database_id)
    assert compare_cleaned_ids(response["id"], session_database_id)
    assert response["object"] == "database"
    assert compare_cleaned_ids(response["parent"]["page_id"], session_page_id)


def test_databases_update(client, session_database_id):
    icon = {"type": "emoji", "emoji": "🔥"}

    response = client.databases.update(database_id=session_database_id, icon=icon)
    assert response["icon"] == icon


def test_comments_list(client, session_page_id, session_comment_id):

    response = client.comments.list(block_id=session_page_id)

    assert response["object"] == "list"
    assert response["results"]
    assert response["results"][0]["object"] == "comment"
    assert response["results"][0]["id"] == session_comment_id
