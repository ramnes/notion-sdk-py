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


def test_api_response_error_additional_data():
    import httpx

    class DummyResponse:
        status_code = 400
        headers = {}
        text = '{"object": "error", "message": "msg", "code": "validation_error", "additional_data": {"foo": "bar"}}'

        def json(self):
            return {
                "object": "error",
                "message": "msg",
                "code": "validation_error",
                "additional_data": {"foo": "bar"},
            }

    response = DummyResponse()
    err = APIResponseError(
        response, "msg", "validation_error", additional_data={"foo": "bar"}
    )
    assert err.additional_data == {"foo": "bar"}
    assert "foo" in str(err)


def test_api_response_error_without_additional_data():
    """Test APIResponseError __str__ method without additional_data"""
    import httpx

    class DummyResponse:
        status_code = 400
        headers = {}
        text = (
            '{"object": "error", "message": "Test error", "code": "validation_error"}'
        )

        def json(self):
            return {
                "object": "error",
                "message": "Test error",
                "code": "validation_error",
            }

    response = DummyResponse()
    err = APIResponseError(response, "Test error", "validation_error")

    error_str = str(err)
    assert "additional_data" not in error_str
    assert "Test error" in error_str


async def test_is_api_error_code():
    error_code = "unauthorized"
    assert is_api_error_code(error_code)
    assert not is_api_error_code(None)
    assert not is_api_error_code(404)
