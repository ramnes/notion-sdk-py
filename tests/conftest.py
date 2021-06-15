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
        "filter_headers": [("authorization", "secret_...")],
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
