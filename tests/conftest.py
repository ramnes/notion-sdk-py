import os
import re
from datetime import datetime
from typing import Any, Dict, Generator, Optional

import pytest

from notion_client import AsyncClient, Client


@pytest.fixture(scope="session")
def vcr_config() -> Dict[str, Any]:
    def remove_headers(response: Dict[str, Any]) -> Dict[str, Any]:
        headers_to_keep: Dict[str, Any] = {}
        if response.get("headers"):
            for key, value in response["headers"].items():
                key_lower = key.lower()
                if key_lower in ["content-type", "content-encoding", "content-length"]:
                    headers_to_keep[key] = value

        response["headers"] = headers_to_keep
        return response

    return {
        "filter_headers": [
            ("authorization", "ntn_..."),
            ("user-agent", None),
            ("cookie", None),
        ],
        "before_record_response": remove_headers,
        "match_on": ["method", "remove_page_id_for_matches"],
        "decode_compressed_response": False,
    }


@pytest.fixture(scope="module")
def vcr(vcr):
    def remove_page_id_for_matches(r1, r2):
        RE_PAGE_ID = r"[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}"
        uri1 = str(getattr(r1, "uri", r1))
        uri2 = str(getattr(r2, "uri", r2))
        return re.sub(RE_PAGE_ID, "", uri1) == re.sub(RE_PAGE_ID, "", uri2)

    vcr.register_matcher("remove_page_id_for_matches", remove_page_id_for_matches)
    return vcr


@pytest.fixture(scope="session")
def token() -> Optional[str]:
    return os.environ.get("NOTION_TOKEN")


@pytest.fixture(scope="module", autouse=True)
def parent_page_id(vcr) -> str:
    """this is the ID of the Notion page where the tests will be executed
    the bot must have access to the page with all the capabilities enabled"""
    page_id = os.environ.get("NOTION_TEST_PAGE_ID")
    if page_id:
        return page_id

    try:
        with vcr.use_cassette("test_pages_create.yaml") as cass:
            response = cass._serializer.deserialize(cass.data[0][1]["content"])
            return response["parent"]["page_id"]
    except Exception:
        return "26899f72bada80dc843deacaf51e89ad"


@pytest.fixture(scope="function")
def page_id(client, parent_page_id):
    """create a temporary subpage inside parent_page_id to run tests without leaks"""
    response = client.pages.create(
        parent={"page_id": parent_page_id},
        properties={
            "title": [{"text": {"content": f"Test {datetime.now()}"}}],
        },
        children=[],
    )

    yield response["id"]
    client.blocks.delete(block_id=response["id"])


@pytest.fixture(scope="function")
def block_id(client, page_id) -> str:
    """create a block inside page_id to run each block test without leaks"""
    children = [
        {"paragraph": {"rich_text": [{"text": {"content": "I'm a paragraph."}}]}}
    ]

    response = client.blocks.children.append(block_id=page_id, children=children)
    yield response["results"][0]["id"]
    client.blocks.delete(block_id=response["results"][0]["id"])


@pytest.fixture(scope="function")
def database_id(client, page_id) -> str:
    """create a block inside page_id to run each database test without leaks"""
    db_name = f"Test Database - {datetime.now()}"
    properties = {
        "Name": {"title": {}},  # required property
    }
    title = [{"type": "text", "text": {"content": db_name}}]
    parent = {"type": "page_id", "page_id": page_id}
    response = client.databases.create(
        **{"parent": parent, "title": title, "properties": properties}
    )

    yield response["id"]
    client.blocks.delete(block_id=response["id"])


@pytest.fixture(scope="function")
def comment_id(client, page_id) -> str:
    """create a comment inside page_id to run each comment test without leaks"""
    parent = {"page_id": page_id}
    rich_text = [
        {
            "text": {
                "content": "This is a test comment.",
            },
        },
    ]

    response = client.comments.create(parent=parent, rich_text=rich_text)

    yield response["id"]


text_block_id = block_id


@pytest.fixture(scope="function")
def equation_block_id(client, page_id) -> str:
    """create a block inside page_id that has an equation"""
    children = [
        {"paragraph": {"rich_text": [{"equation": {"expression": "E = mc^2"}}]}}
    ]

    response = client.blocks.children.append(block_id=page_id, children=children)
    yield response["results"][0]["id"]
    client.blocks.delete(block_id=response["results"][0]["id"])


@pytest.fixture(scope="function")
def mention_block_id(client, page_id) -> str:
    """create a block inside page_id that has a date mention"""
    children = [
        {
            "paragraph": {
                "rich_text": [
                    {
                        "mention": {
                            "type": "date",
                            "date": {"start": "2022-12-16", "end": None},
                        }
                    }
                ]
            }
        }
    ]

    response = client.blocks.children.append(block_id=page_id, children=children)
    yield response["results"][0]["id"]
    client.blocks.delete(block_id=response["results"][0]["id"])


@pytest.fixture(scope="module")
def client(token: Optional[str]):
    with Client({"auth": token}) as client:
        yield client


@pytest.fixture
async def async_client(token: Optional[str]):
    async with AsyncClient({"auth": token}) as client:
        yield client
