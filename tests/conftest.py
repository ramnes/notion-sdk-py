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
    return os.getenv("NOTION_TOKEN")


@pytest.fixture
def client(token):
    return Client({"auth": token})


@pytest.fixture
async def async_client(token):
    client = AsyncClient({"auth": token})
    yield client
    await client.aclose()
