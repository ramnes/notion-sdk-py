import pytest


# USERS
def test_users_list(client):
    response = client.users.list()
    assert response["results"]
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


# DATABASES

# this will be a fixture because I need the ID of the temporary DB for the other tests


@pytest.fixture
def database_for_tests(client, database):
    response = client.databases.create(**database)
    assert response
    assert response["id"]
    # TODO: maybe we should just return the ID?
    return response


def test_databases_retrieve(client, database_for_tests, testing_page):
    def clean_url(url) -> str:
        return url.replace("-", "").strip()

    db_id = database_for_tests["id"]
    response = client.databases.retrieve(db_id)
    assert response
    assert clean_url(response["id"]) == clean_url(db_id)
    assert response["object"] == "database"
    assert clean_url(response["parent"]["page_id"]) == clean_url(testing_page)
    # TODO: add tests on properties


def test_databases_query(client, database_for_tests):
    db_id = database_for_tests["id"]
    query = {
        "database_id": db_id,
        "filter": {"timestamp": "created_time", "created_time": {"past_week": {}}},
    }

    response = client.databases.query(**query)
    assert response
    assert response["object"] == "list"
    # results should be empty
    assert not response["results"]


def test_databases_update(client, database_for_tests):
    db_id = database_for_tests["id"]
    icon = {"type": "emoji", "emoji": "🔥"}

    response = client.databases.update(database_id=db_id, icon=icon)
    assert response
    assert response["icon"] == icon
