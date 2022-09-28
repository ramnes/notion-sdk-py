from datetime import datetime

import pytest

TEST_PAGE_NAME = f"Test Page - {datetime.now()}"


def compare_cleaned_ids(id1: str, id2: str) -> bool:
    return id1.replace("-", "").strip() == id2.replace("-", "").strip()


# PAGES
# `test_pages_create` generates a temporary page and uses its ID
# as input for all the other tests. Their objects (databases, blocks, comments)
# will be created inside the page. With this method we have a
# unique environment for each run, using the current datetime as identifier


@pytest.fixture(scope="session")
def test_pages_create(client, testing_page) -> str:
    response = client.pages.create(
        parent={"page_id": testing_page},
        properties={
            "title": [{"text": {"content": TEST_PAGE_NAME}}],
        },
        # using children = [] for avoiding issue with the Notion API
        # when creating a subpage without blocks
        children=[],
    )

    yield response["id"]

    # at the end of the session, delete the page
    client.blocks.delete(block_id=response["id"])


def test_pages_retrieve(client, test_pages_create, testing_page):
    response = client.pages.retrieve(page_id=test_pages_create)
    assert response["object"] == "page"
    assert compare_cleaned_ids(response["parent"]["page_id"], testing_page)


def test_pages_update(client, test_pages_create):
    icon = {"type": "emoji", "emoji": "🛴"}

    response = client.pages.update(page_id=test_pages_create, icon=icon)
    assert response["icon"] == icon


def test_pages_properties_retrieve(client, test_pages_create):
    response = client.pages.properties.retrieve(
        page_id=test_pages_create, property_id="title"
    )
    assert response["results"][0]["type"] == "title"


# BLOCKS
# `test_blocks_children_append` generates a temporary pragaraph
# and uses its ID as input for the other tests


@pytest.fixture(scope="session")
def test_blocks_children_append(client, test_pages_create):
    children = [
        {"paragraph": {"rich_text": [{"text": {"content": "I'm a paragraph."}}]}}
    ]

    response = client.blocks.children.append(
        block_id=test_pages_create, children=children
    )
    assert response["type"] == "block"
    assert response["results"][0]["type"] == "paragraph"

    return response["results"][0]["id"]


def test_blocks_children_list(client, test_pages_create, test_blocks_children_append):
    response = client.blocks.children.list(block_id=test_pages_create)
    assert response["object"] == "list"
    assert response["type"] == "block"
    assert compare_cleaned_ids(
        response["results"][0]["id"], test_blocks_children_append
    )


def test_blocks_retrieve(client, test_blocks_children_append):
    response = client.blocks.retrieve(block_id=test_blocks_children_append)
    assert response["object"] == "block"
    assert response["type"] == "paragraph"
    assert compare_cleaned_ids(response["id"], test_blocks_children_append)


def test_blocks_update(client, test_blocks_children_append):
    new_plain_text = "I'm an updated paragraph."
    new_text = {
        "rich_text": [
            {
                "text": {"content": new_plain_text},
                "annotations": {"bold": True, "color": "red_background"},
            }
        ]
    }
    response = client.blocks.update(
        block_id=test_blocks_children_append, paragraph=new_text
    )

    assert compare_cleaned_ids(response["id"], test_blocks_children_append)
    assert response["paragraph"]["rich_text"][0]["plain_text"] == new_plain_text


def test_blocks_delete(client, test_pages_create, test_blocks_children_append):
    response = client.blocks.delete(block_id=test_blocks_children_append)

    assert compare_cleaned_ids(response["id"], test_blocks_children_append)

    new_retrieve = client.blocks.retrieve(block_id=test_blocks_children_append)
    assert new_retrieve["archived"]


# USERS


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


# SEARCH
def test_search(client, test_pages_create):
    payload = {
        "query": TEST_PAGE_NAME,
        "sort": {
            "direction": "ascending",
            "timestamp": "last_edited_time",
        },
    }

    response = client.search(**payload)
    assert response["results"]
    assert response["results"][0]["id"] == test_pages_create


# DATABASES
# `test_databases_create` generates a temporary database
# and uses its ID as input for the other tests


@pytest.fixture(scope="session")
def test_databases_create(client, test_pages_create) -> str:
    db_name = f"Test Database - {datetime.now()}"
    properties = {
        "Name": {"title": {}},  # required property
    }
    title = [{"type": "text", "text": {"content": db_name}}]
    parent = {"type": "page_id", "page_id": test_pages_create}
    response = client.databases.create(
        **{"parent": parent, "title": title, "properties": properties}
    )

    #  the test returns the ID of the newly created database for the other tests
    return response["id"]


def test_databases_query(client, test_databases_create):
    query = {
        "database_id": test_databases_create,
        "filter": {"timestamp": "created_time", "created_time": {"past_week": {}}},
    }

    response = client.databases.query(**query)
    assert response["object"] == "list"
    # results should be empty, the testing DB has no rows
    assert not response["results"]


def test_databases_retrieve(client, test_databases_create, test_pages_create):

    response = client.databases.retrieve(test_databases_create)
    assert compare_cleaned_ids(response["id"], test_databases_create)
    assert response["object"] == "database"
    assert compare_cleaned_ids(response["parent"]["page_id"], test_pages_create)


def test_databases_update(client, test_databases_create):
    icon = {"type": "emoji", "emoji": "🔥"}

    response = client.databases.update(database_id=test_databases_create, icon=icon)
    assert response["icon"] == icon


# COMMENTS
# `test_comments_create` generates a temporary comment
# and uses its ID as input for the other test


@pytest.fixture(scope="session")
def test_comments_create(client, test_pages_create) -> str:
    parent = {"page_id": test_pages_create}
    rich_text = [
        {
            "text": {
                "content": "This is a test comment.",
            },
        },
    ]

    response = client.comments.create(parent=parent, rich_text=rich_text)

    assert response["object"] == "comment"
    assert compare_cleaned_ids(response["parent"]["page_id"], test_pages_create)
    assert response["rich_text"][0]["plain_text"] == rich_text[0]["text"]["content"]

    return response["id"]


def test_comments_list(client, test_pages_create, test_comments_create):

    response = client.comments.list(block_id=test_pages_create)

    assert response["object"] == "list"
    assert response["results"]
    assert response["results"][0]["object"] == "comment"
    assert response["results"][0]["id"] == test_comments_create
