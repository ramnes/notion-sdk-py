import os
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
def token() -> str:
    notion_token = os.environ.get("NOTION_TOKEN")
    if not notion_token:
        raise EnvironmentError("Env variable NOTION_TOKEN needed for testing")
    return notion_token


@pytest.fixture(scope="session")
def testing_page() -> str:
    """this is the URL of the Notion page where the tests will be executed
    the bot must have access to the page with all the capabilities enabled"""
    page = os.environ.get("NOTION_TESTING_URL")
    if not page:
        raise EnvironmentError("Env variable NOTION_TESTING_URL needed for testing")
    return page


@pytest.fixture(scope="session")
def client(token: Optional[str]):
    return Client({"auth": token})


@pytest.fixture
async def async_client(token: Optional[str]):
    client = AsyncClient({"auth": token})
    yield client
    await client.aclose()
