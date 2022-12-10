import pytest

from notion_client import AsyncClient, Client
from notion_client.errors import (
    APIResponseError,
    HTTPResponseError,
    RequestTimeoutError,
    is_api_error_code,
)

STATUS_PAGE_BAD_REQUEST = "https://httpstat.us/400"
STATUS_PAGE_TIMEOUT = "https://httpstat.us/200?sleep=100"


@pytest.mark.vcr()
def test_api_response_error(client):
    with pytest.raises(APIResponseError):
        client.request("/invalid", "GET")
    with pytest.raises(APIResponseError):
        client.request("/invalid", "GET", auth="Invalid")


def test_api_request_timeout_error(token):
    client = Client({"auth": token, "timeout_ms": 1})

    with pytest.raises(RequestTimeoutError):
        client.request(STATUS_PAGE_TIMEOUT, "GET")


@pytest.mark.vcr()
def test_api_http_response_error(client):
    with pytest.raises(HTTPResponseError):
        client.request(STATUS_PAGE_BAD_REQUEST, "GET")


@pytest.mark.vcr()
async def test_async_api_response_error(async_client):
    with pytest.raises(APIResponseError):
        await async_client.request("/invalid", "GET")
    with pytest.raises(APIResponseError):
        await async_client.request("/invalid", "GET", auth="Invalid")


async def test_async_api_request_timeout_error(token):
    async_client = AsyncClient({"auth": token, "timeout_ms": 1})

    with pytest.raises(RequestTimeoutError):
        await async_client.request(STATUS_PAGE_TIMEOUT, "GET")


@pytest.mark.vcr()
async def test_api_async_request_bad_request_error(async_client):
    with pytest.raises(HTTPResponseError):
        await async_client.request(STATUS_PAGE_BAD_REQUEST, "GET")


async def test_is_api_error_code():
    error_code = "unauthorized"
    assert is_api_error_code(error_code)
    assert not is_api_error_code(None)
    assert not is_api_error_code(404)
