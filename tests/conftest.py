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


@pytest.fixture(scope="session")
def client(token: Optional[str]):
    return Client({"auth": token})


@pytest.fixture
async def async_client(token: Optional[str]):
    client = AsyncClient({"auth": token})
    yield client
    await client.aclose()
