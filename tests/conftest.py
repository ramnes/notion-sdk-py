import os
import re
import warnings
from datetime import datetime
from typing import Optional

import pytest

from notion_client import AsyncClient, Client

TEST_PAGE_NAME = f"Test Page - {datetime.now()}"


@pytest.fixture(scope="session")
def vcr_config():
    def remove_headers(response: dict):
        response["headers"] = {}
        return response

    return {
        "filter_headers": [("authorization", "secret_..."), ("user-agent", None)],
        "before_record_response": remove_headers,
        "match_on": ["method", "remove_page_id_for_matches"],
    }


@pytest.fixture(scope="module")
def vcr(vcr):
    def remove_page_id_for_matches(r1, r2):
        RE_PAGE_ID = r"[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}"
        return re.sub(RE_PAGE_ID, r1.uri, "") == re.sub(RE_PAGE_ID, r2.uri, "")

    vcr.register_matcher("remove_page_id_for_matches", remove_page_id_for_matches)
    return vcr


@pytest.fixture(scope="session")
def token() -> str:
    notion_token = os.environ.get("NOTION_TOKEN")
    if not notion_token:
        raise EnvironmentError("Env variable NOTION_TOKEN needed for testing")
    return notion_token


@pytest.fixture(scope="module")
def page_id(vcr) -> str:
    """this is the ID of the Notion page where the tests will be executed
    the bot must have access to the page with all the capabilities enabled"""
    notion_page_id = os.environ.get("NOTION_TEST_PAGE_ID")
    if not notion_page_id:
        warnings.warn(
            """Env variable NOTION_TEST_PAGE_ID needed for testing with new cassettes.
            Retrieving the page_id from existing cassette...
            """
        )

        with vcr.use_cassette("test_pages_create.yaml") as cass:
            response = cass._serializer.deserialize(cass.data[0][1]["content"])
            notion_page_id = response["parent"]["page_id"]

    return notion_page_id


@pytest.fixture(scope="module")
def session_page_id(vcr) -> str:
    """this is the id of the subpage inside page_id where the test session will run"""
    with vcr.use_cassette("test_pages_create.yaml") as cass:
        response = cass._serializer.deserialize(cass.data[0][1]["content"])
        return response["id"]


@pytest.fixture(scope="module")
def session_block_id(vcr) -> str:
    with vcr.use_cassette("test_blocks_children_create.yaml") as cass:
        response = cass._serializer.deserialize(cass.data[0][1]["content"])
        return response["results"][0]["id"]


@pytest.fixture(scope="module")
def session_database_id(vcr) -> str:
    with vcr.use_cassette("test_databases_create.yaml") as cass:
        response = cass._serializer.deserialize(cass.data[0][1]["content"])
        return response["id"]


@pytest.fixture(scope="session")
def client(token: Optional[str]):
    return Client({"auth": token})


@pytest.fixture
async def async_client(token: Optional[str]):
    client = AsyncClient({"auth": token})
    yield client
    await client.aclose()
