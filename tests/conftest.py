import os

import pytest

from notion_client import AsyncClient, Client


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker("asyncio")


@pytest.fixture(scope="session")
def vcr_config():
    def remove_headers(response):
        response["headers"] = {}
        return response

    return {
        "filter_headers": [("authorization", "secret_..."), ("user-agent", None)],
        "before_record_response": remove_headers,
    }


@pytest.fixture(scope="session")
def token():
    return os.environ["NOTION_TOKEN"]


@pytest.fixture
def client(token):
    return Client({"auth": token})


@pytest.fixture
def async_client(token):
    return AsyncClient({"auth": token})


@pytest.fixture
def annotation():
    return {
        "bold": True,
        "italic": False,
        "strikethrough": False,
        "underline": True,
        "code": False,
        "color": "yellow",
    }


@pytest.fixture
def title(annotation):
    return {
        "type": "text",
        "text": {"content": "Test database", "link": None},
        "annotations": annotation,
        "plain_text": "Test database",
        "href": None,
    }


@pytest.fixture
def database_json(title):
    return {
        "object": "database",
        "id": "4efbd42b-534d-42af-a142-c17105a42c07",
        "created_time": "2021-05-28T09:53:15.949Z",
        "last_edited_time": "2021-05-29T07:11:00.000Z",
        "title": [title],
        "properties": {
            "Property": {
                "id": "FnbZ",
                "type": "formula",
                "formula": {"expression": 'prop("Status") == "Complete"'},
            },
            "Website": {"id": "j*,3", "type": "rich_text", "rich_text": {}},
            "Status": {
                "id": "{*I8",
                "type": "select",
                "select": {
                    "options": [
                        {"id": "1", "name": "Not started", "color": "red"},
                        {"id": "2", "name": "Started", "color": "yellow"},
                        {"id": "3", "name": "Completed", "color": "green"},
                        {
                            "id": "2a958772-12c2-4916-8c2c-634fcd1f9a80",
                            "name": "Archived",
                            "color": "gray",
                        },
                    ]
                },
            },
            "Name": {"id": "title", "type": "title", "title": {}},
        },
    }
