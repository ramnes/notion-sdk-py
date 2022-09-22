import os
from datetime import datetime
from typing import Optional

import pytest

from notion_client import AsyncClient, Client


@pytest.fixture(scope="session")
def vcr_config():
    def remove_headers(response: dict):
        response["headers"] = {}
        return response

    return {
        "filter_headers": [("authorization", "secret_..."), ("user-agent", None)],
        "before_record_response": remove_headers,
    }


@pytest.fixture(scope="session")
def token() -> Optional[str]:
    return os.getenv("NOTION_TOKEN")


@pytest.fixture(scope="session")
def testing_page() -> Optional[str]:
    # TODO: clean the page at the beginning of the tests?
    # wbut hat if multiple people are running tests on the page?
    # create a subpage for every concurrent run?
    # right now there will be a new sub-page on the testing URL for every run
    # we can maybe delete subpages older than 1 day
    return os.getenv("NOTION_TESTING_URL")


@pytest.fixture
def client(token: Optional[str]):
    return Client({"auth": token})


@pytest.fixture
async def async_client(token: Optional[str]):
    client = AsyncClient({"auth": token})
    yield client
    await client.aclose()


@pytest.fixture
def database(testing_page):
    """I need to temporarily create a database for testing the endpoint
    the name will be the current timestamp"""
    db_name = f"Test - {datetime.now()}"
    # properties taken from the examples folder
    db_properties = {
        "Name": {"title": {}},  # required property, leave it empty
        "In stock": {"checkbox": {}},
        "Food group": {
            "select": {
                "options": [
                    {"name": "🥦 Vegetable", "color": "green"},
                    {"name": "🍎 Fruit", "color": "red"},
                    {"name": "💪 Protein", "color": "yellow"},
                ]
            }
        },
        "Price": {"number": {"format": "dollar"}},
        "Last ordered": {"date": {}},
        "Store availability": {
            "type": "multi_select",
            "multi_select": {
                "options": [
                    {"name": "Duc Loi Market", "color": "blue"},
                    {"name": "Rainbow Grocery", "color": "gray"},
                    {"name": "Nijiya Market", "color": "purple"},
                    {"name": "Gus's Community Market", "color": "yellow"},
                ]
            },
        },
        "+1": {"people": {}},
        "Photo": {"files": {}},
    }
    title = [{"type": "text", "text": {"content": db_name}}]
    parent = {"type": "page_id", "page_id": testing_page}
    return {"parent": parent, "title": title, "properties": db_properties}
