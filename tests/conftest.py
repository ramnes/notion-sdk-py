import os
import re
from datetime import datetime
from typing import Optional

import pytest

from notion_client import AsyncClient, Client
from dotenv import load_dotenv

load_dotenv()


# Fix for VCR compatibility issue with cassettes that have gzip content
def _patch_vcr_from_serialized_response():
    """Patch VCR's _from_serialized_response to handle missing content field."""
    try:
        import vcr.stubs.httpx_stubs
        from unittest.mock import patch, MagicMock
        import httpx

        @patch("httpx.Response.close", MagicMock())
        @patch("httpx.Response.read", MagicMock())
        def _patched_from_serialized_response(
            request, serialized_response, history=None
        ):
            # Handle the case where content is None but body.string exists
            content = serialized_response.get("content")
            if content is None:
                # Try to get content from body.string (for older cassettes)
                body = serialized_response.get("body", {})
                if isinstance(body, dict) and "string" in body:
                    body_string = body["string"]
                    if isinstance(body_string, bytes):
                        content = body_string
                    else:
                        content = body_string.encode() if body_string else b""
                else:
                    content = b""
            elif isinstance(content, str):
                content = content.encode()
            elif content is None:
                content = b""

            # Handle status_code - check both new and old format
            status_code = serialized_response.get("status_code")
            if status_code is None:
                # Try to get from status.code (older cassettes format)
                status = serialized_response.get("status", {})
                if isinstance(status, dict):
                    status_code = status.get("code", 200)
                else:
                    status_code = 200

            response = httpx.Response(
                status_code=status_code,
                request=request,
                headers=vcr.stubs.httpx_stubs._from_serialized_headers(
                    serialized_response.get("headers")
                ),
                content=content,
                history=history or [],
            )
            response._content = content
            return response

        # Apply the patch
        vcr.stubs.httpx_stubs._from_serialized_response = (
            _patched_from_serialized_response
        )

    except ImportError:
        # VCR not available, skip patching
        pass


# Apply the patch when the module is imported
_patch_vcr_from_serialized_response()


@pytest.fixture(scope="session")
def vcr_config():
    def remove_headers(response: dict):
        headers_to_keep = {}
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
        try:
            RE_PAGE_ID = r"[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}"
            # Get URI strings safely
            uri1 = str(getattr(r1, "uri", r1))
            uri2 = str(getattr(r2, "uri", r2))
            # Remove page IDs from URIs before comparing
            uri1_clean = re.sub(RE_PAGE_ID, "", uri1)
            uri2_clean = re.sub(RE_PAGE_ID, "", uri2)
            return uri1_clean == uri2_clean
        except Exception:
            # If anything goes wrong, fall back to exact URI comparison
            return str(getattr(r1, "uri", r1)) == str(getattr(r2, "uri", r2))

    vcr.register_matcher("remove_page_id_for_matches", remove_page_id_for_matches)
    return vcr


@pytest.fixture(scope="session")
def token() -> str:
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
        pytest.exit(
            "Missing base page id. Restore test_pages_create.yaml or add "
            "NOTION_TEST_PAGE_ID to your environment.",
        )


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
