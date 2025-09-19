import pytest
from httpx import TimeoutException

from notion_client.errors import (
    APIResponseError,
    HTTPResponseError,
    RequestTimeoutError,
    is_api_error_code,
)

STATUS_PAGE_BAD_REQUEST = "https://mock.httpstatus.io/400"


@pytest.mark.vcr()
def test_api_response_error(client):
    with pytest.raises(APIResponseError):
        client.request("/invalid", "GET")
    with pytest.raises(APIResponseError):
        client.request("/users", "GET", auth="Invalid")


def test_api_request_timeout_error(monkeypatch, client):
    def mock_timeout_request(*args):
        raise TimeoutException("Mock Timeout")

    monkeypatch.setattr(client.client, "send", mock_timeout_request)

    with pytest.raises(RequestTimeoutError):
        client.request("/users", "GET")


@pytest.mark.vcr()
def test_api_http_response_error(client):
    with pytest.raises(HTTPResponseError):
        client.request(STATUS_PAGE_BAD_REQUEST, "GET")


@pytest.mark.vcr()
async def test_async_api_response_error(async_client):
    with pytest.raises(APIResponseError):
        await async_client.request("/invalid", "GET")
    with pytest.raises(APIResponseError):
        await async_client.request("/users", "GET", auth="Invalid")


async def test_async_api_request_timeout_error(monkeypatch, async_client):
    def mock_timeout_request(*args):
        raise TimeoutException("Mock Timeout")

    monkeypatch.setattr(async_client.client, "send", mock_timeout_request)

    with pytest.raises(RequestTimeoutError):
        await async_client.request("/users", "GET")


@pytest.mark.vcr()
async def test_api_async_request_bad_request_error(async_client):
    with pytest.raises(HTTPResponseError):
        await async_client.request(STATUS_PAGE_BAD_REQUEST, "GET")


@pytest.mark.vcr()
async def test_async_api_response_error_additional_data(async_client):
    with pytest.raises(APIResponseError) as exc_info:
        await async_client.request("/users", "GET", auth="invalid-token")

    error = exc_info.value
    assert error.request_id is not None
    if error.additional_data is not None:
        assert isinstance(error.additional_data, dict)


@pytest.mark.vcr()
def test_api_response_error_additional_data(client):
    with pytest.raises(APIResponseError) as exc_info:
        client.request("/users", "GET", auth="invalid-token")

    error = exc_info.value
    assert error.request_id is not None
    if error.additional_data is not None:
        assert isinstance(error.additional_data, dict)


@pytest.mark.vcr()
def test_api_response_error_request_id(client):
    with pytest.raises(APIResponseError) as exc_info:
        client.request("/invalid", "GET")

    error = exc_info.value
    assert error.request_id is not None
    assert isinstance(error.request_id, str)


@pytest.mark.vcr()
async def test_async_api_response_error_request_id(async_client):
    with pytest.raises(APIResponseError) as exc_info:
        await async_client.request("/invalid", "GET")

    error = exc_info.value
    assert error.request_id is not None
    assert isinstance(error.request_id, str)


async def test_is_api_error_code():
    error_code = "unauthorized"
    assert is_api_error_code(error_code)
    assert not is_api_error_code(None)
    assert not is_api_error_code(404)
