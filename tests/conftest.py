import os
from typing import List, Optional

import pytest

from notion_client import AsyncClient, Client


def pytest_collection_modifyitems(items: List[pytest.Item]):
    for item in items:
        item.add_marker("asyncio")


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


@pytest.fixture
def client(token: Optional[str]):
    return Client({"auth": token})


@pytest.fixture
async def async_client(token: Optional[str]):
    client = AsyncClient({"auth": token})
    yield client
    await client.aclose()
