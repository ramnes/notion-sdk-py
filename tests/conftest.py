import os
import re
from datetime import datetime
from typing import Optional
import json

import pytest
from vcr.request import Request

from notion_client import AsyncClient, Client


@pytest.fixture(scope="session")
def vcr_config():
    def remove_headers(response: dict):
        response["headers"] = {}
        return response

    def scrub_requests(request: dict):
        if request.body:
            try:
                body_str = request.body.decode("utf-8")
                body_json = json.loads(body_str)
                if "token" in body_json:
                    body_json["token"] = "ntn_..."
                if "code" in body_json:
                    body_json["code"] = "..."
                if "redirect_uri" in body_json:
                    body_json["redirect_uri"] = "http://..."
                request.body = json.dumps(body_json).encode("utf-8")
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(
                    f"Failed to decode request body: {request.body} \n Error occurred at {e.pos} with message: {e.msg}",
                    request.body,
                    e.pos,
                )
        return request

    def scrub_response(response: dict):
        if "content" in response:
            content = response["content"]
            # Like the case tests/cassettes/test_api_async_request_bad_request_error.yaml, where the response is just a string, not JSON
            # We don't want to raise an error here because the response is not JSON and that is ok
            if "{" not in content:
                return response
            try:
                content_json = json.loads(content)
                if "access_token" in content_json:
                    response["content"] = json.dumps(
                        {key: "..." for key in content_json}, separators=(",", ":")
                    )
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(
                    f"Failed to decode response body: {response["content"]} \n Error occurred at {e.pos} with message: {e.msg}",
                    response["content"],
                    e.pos,
                )
        return response

    # The VCR config requires the passing of the request parameter, despite the face that it is not used
    # (https://vcrpy.readthedocs.io/en/latest/advanced.html#advanced-use-of-filter-headers-filter-query-parameters-and-filter-post-data-parameters)
    def scrub_auth_header(key: str, value: str, request: Optional[Request]):
        if key == "authorization":
            if value.startswith("Bearer "):
                return "ntn_..."
            elif value.startswith("Basic "):
                return 'Basic "Base64Encoded($client_id:$client_secret)"'

    return {
        "filter_headers": [
            ("authorization", scrub_auth_header),
            ("user-agent", None),
            ("cookie", None),
        ],
        "before_record_request": scrub_requests,
        "before_record_response": (remove_headers, scrub_response),
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
    return os.environ.get("NOTION_TOKEN")


@pytest.fixture(scope="session")
def code() -> str:
    return os.environ.get("NOTION_CODE")


@pytest.fixture(scope="session")
def redirect_uri() -> str:
    return os.environ.get("NOTION_REDIRECT_URI")


@pytest.fixture(scope="session")
def client_id() -> str:
    return os.environ.get("NOTION_CLIENT_ID")


@pytest.fixture(scope="session")
def client_secret() -> str:
    return os.environ.get("NOTION_CLIENT_SECRET")


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
