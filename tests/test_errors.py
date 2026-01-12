import pytest
from httpx import TimeoutException
import httpx
import asyncio

from notion_client.errors import (
    APIErrorCode,
    ClientErrorCode,
    is_notion_client_error,
    is_notion_client_error_with_code,
    RequestTimeoutError,
    HTTPResponseError,
    is_http_response_error,
    UnknownHTTPResponseError,
    APIResponseError,
    build_request_error,
    _parse_api_error_response_body,
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
def test_api_response_error_request_id(client):
    with pytest.raises(APIResponseError) as exc_info:
        client.request("/invalid", "GET")

    error = exc_info.value
    assert isinstance(error.request_id, str)


@pytest.mark.vcr()
async def test_async_api_response_error_request_id(async_client):
    with pytest.raises(APIResponseError) as exc_info:
        await async_client.request("/invalid", "GET")

    error = exc_info.value
    assert isinstance(error.request_id, str)


@pytest.mark.vcr()
def test_api_response_error_additional_data(client):
    with pytest.raises(APIResponseError) as exc_info:
        client.request("/users", "GET", auth="invalid-token")

    error = exc_info.value
    if error.additional_data is not None:
        assert isinstance(error.additional_data, dict)


@pytest.mark.vcr()
async def test_async_api_response_error_additional_data(async_client):
    with pytest.raises(APIResponseError) as exc_info:
        await async_client.request("/users", "GET", auth="invalid-token")

    error = exc_info.value
    if error.additional_data is not None:
        assert isinstance(error.additional_data, dict)


async def test_is_api_error_code():
    error_code = "unauthorized"
    assert is_api_error_code(error_code)
    assert not is_api_error_code(None)
    assert not is_api_error_code(404)


def test_is_notion_client_error():
    """Test is_notion_client_error function."""
    timeout_error = RequestTimeoutError()
    assert is_notion_client_error(timeout_error)

    unknown_error = UnknownHTTPResponseError(status=500)
    assert is_notion_client_error(unknown_error)

    api_error = APIResponseError(
        code=APIErrorCode.ObjectNotFound,
        status=404,
        message="Not found",
        headers=httpx.Headers(),
        raw_body_text="{}",
    )
    assert is_notion_client_error(api_error)

    assert not is_notion_client_error(Exception("generic error"))
    assert not is_notion_client_error(None)
    assert not is_notion_client_error("error string")
    assert not is_notion_client_error(404)


def test_is_notion_client_error_with_code():
    """Test is_notion_client_error_with_code function."""
    timeout_error = RequestTimeoutError()
    assert is_notion_client_error_with_code(
        timeout_error, {ClientErrorCode.RequestTimeout.value: True}
    )
    assert not is_notion_client_error_with_code(
        timeout_error, {ClientErrorCode.ResponseError.value: True}
    )

    unknown_error = UnknownHTTPResponseError(status=500)
    assert is_notion_client_error_with_code(
        unknown_error, {ClientErrorCode.ResponseError.value: True}
    )

    api_error = APIResponseError(
        code=APIErrorCode.ObjectNotFound,
        status=404,
        message="Not found",
        headers=httpx.Headers(),
        raw_body_text="{}",
    )
    assert is_notion_client_error_with_code(
        api_error, {APIErrorCode.ObjectNotFound.value: True}
    )

    assert not is_notion_client_error_with_code(
        None, {ClientErrorCode.RequestTimeout.value: True}
    )
    assert not is_notion_client_error_with_code(
        "error", {ClientErrorCode.RequestTimeout.value: True}
    )


def test_is_http_response_error():
    """Test is_http_response_error function."""
    unknown_error = UnknownHTTPResponseError(status=500)
    assert is_http_response_error(unknown_error)

    for api_code in APIErrorCode:
        api_error = APIResponseError(
            code=api_code,
            status=400,
            message="Test error",
            headers=httpx.Headers(),
            raw_body_text="{}",
        )
        assert is_http_response_error(api_error), f"Failed for {api_code}"

    timeout_error = RequestTimeoutError()
    assert not is_http_response_error(timeout_error)

    assert not is_http_response_error(None)
    assert not is_http_response_error("error")
    assert not is_http_response_error(Exception("generic"))


def test_request_timeout_error_static_method():
    """Test RequestTimeoutError.is_request_timeout_error static method."""
    timeout_error = RequestTimeoutError()
    assert RequestTimeoutError.is_request_timeout_error(timeout_error)

    unknown_error = UnknownHTTPResponseError(status=500)
    assert not RequestTimeoutError.is_request_timeout_error(unknown_error)

    api_error = APIResponseError(
        code=APIErrorCode.ObjectNotFound,
        status=404,
        message="Not found",
        headers=httpx.Headers(),
        raw_body_text="{}",
    )
    assert not RequestTimeoutError.is_request_timeout_error(api_error)

    assert not RequestTimeoutError.is_request_timeout_error(None)
    assert not RequestTimeoutError.is_request_timeout_error("error")


def test_unknown_http_response_error_static_method():
    """Test UnknownHTTPResponseError.is_unknown_http_response_error static method."""
    unknown_error = UnknownHTTPResponseError(status=500)
    assert UnknownHTTPResponseError.is_unknown_http_response_error(unknown_error)

    timeout_error = RequestTimeoutError()
    assert not UnknownHTTPResponseError.is_unknown_http_response_error(timeout_error)

    api_error = APIResponseError(
        code=APIErrorCode.ObjectNotFound,
        status=404,
        message="Not found",
        headers=httpx.Headers(),
        raw_body_text="{}",
    )
    assert not UnknownHTTPResponseError.is_unknown_http_response_error(api_error)

    assert not UnknownHTTPResponseError.is_unknown_http_response_error(None)


def test_api_response_error_static_method():
    """Test APIResponseError.is_api_response_error static method."""
    for api_code in APIErrorCode:
        api_error = APIResponseError(
            code=api_code,
            status=400,
            message="Test error",
            headers=httpx.Headers(),
            raw_body_text="{}",
        )
        assert APIResponseError.is_api_response_error(
            api_error
        ), f"Failed for {api_code}"

    timeout_error = RequestTimeoutError()
    assert not APIResponseError.is_api_response_error(timeout_error)

    unknown_error = UnknownHTTPResponseError(status=500)
    assert not APIResponseError.is_api_response_error(unknown_error)

    assert not APIResponseError.is_api_response_error(None)


@pytest.mark.vcr()
def test_build_request_error_integration(client):
    """Test build_request_error integration with actual API error response."""
    invalid_page_id = "00000000-0000-0000-0000-000000000000"

    with pytest.raises(APIResponseError) as exc_info:
        client.pages.retrieve(invalid_page_id)

    error = exc_info.value

    assert isinstance(error, APIResponseError)
    assert error.code == APIErrorCode.ObjectNotFound
    assert error.status == 404
    assert error.body


def test_build_request_error_creates_api_response_error():
    """Test build_request_error successfully creates APIResponseError for valid API errors."""
    body_text = '{"code": "object_not_found", "message": "Object not found"}'
    response = httpx.Response(
        status_code=404,
        headers=httpx.Headers(),
        content=body_text.encode(),
    )
    error = build_request_error(response, body_text)
    assert isinstance(error, APIResponseError)
    assert error.code == APIErrorCode.ObjectNotFound
    assert error.status == 404

    body_text = """{
        "code": "validation_error",
        "message": "Validation failed",
        "additional_data": {"errors": ["field1", "field2"]}
    }"""
    response = httpx.Response(
        status_code=400,
        headers=httpx.Headers(),
        content=body_text.encode(),
    )
    error = build_request_error(response, body_text)
    assert isinstance(error, APIResponseError)
    assert error.code == APIErrorCode.ValidationError
    assert error.additional_data == {"errors": ["field1", "field2"]}

    body_text = """{
        "code": "rate_limited",
        "message": "Rate limited",
        "request_id": "abc-123-def"
    }"""
    response = httpx.Response(
        status_code=429,
        headers=httpx.Headers(),
        content=body_text.encode(),
    )
    error = build_request_error(response, body_text)
    assert isinstance(error, APIResponseError)
    assert error.code == APIErrorCode.RateLimited
    assert error.request_id == "abc-123-def"

    for api_code in APIErrorCode:
        body_text = f'{{"code": "{api_code.value}", "message": "Test message"}}'
        response = httpx.Response(
            status_code=400,
            headers=httpx.Headers(),
            content=body_text.encode(),
        )
        error = build_request_error(response, body_text)
        assert isinstance(error, APIResponseError), f"Failed for {api_code}"
        assert error.code == api_code, f"Failed for {api_code}"


def test_build_request_error_creates_unknown_http_response_error():
    """Test build_request_error creates UnknownHTTPResponseError for invalid responses."""
    response = httpx.Response(
        status_code=500,
        headers=httpx.Headers(),
        content=b"Internal Server Error",
    )
    error = build_request_error(response, "Internal Server Error")
    assert isinstance(error, UnknownHTTPResponseError)
    assert error.code == ClientErrorCode.ResponseError.value
    assert error.status == 500

    body_text = '{"code": "unknown_error", "message": "Unknown error"}'
    response = httpx.Response(
        status_code=500,
        headers=httpx.Headers(),
        content=body_text.encode(),
    )
    error = build_request_error(response, body_text)
    assert isinstance(error, UnknownHTTPResponseError)
    assert error.status == 500

    error = build_request_error(response, '["array", "not", "dict"]')
    assert isinstance(error, UnknownHTTPResponseError)

    body_text = '{"code": "object_not_found"}'
    response = httpx.Response(
        status_code=404,
        headers=httpx.Headers(),
        content=body_text.encode(),
    )
    error = build_request_error(response, body_text)
    assert isinstance(error, UnknownHTTPResponseError)

    body_text = '{"code": "object_not_found", "message": 123}'
    response = httpx.Response(
        status_code=404,
        headers=httpx.Headers(),
        content=body_text.encode(),
    )
    error = build_request_error(response, body_text)
    assert isinstance(error, UnknownHTTPResponseError)


def test_unknown_http_response_error_default_message():
    """Test UnknownHTTPResponseError generates default message."""
    error = UnknownHTTPResponseError(status=503)

    assert error.status == 503
    assert "503" in str(error)
    assert error.code == ClientErrorCode.ResponseError.value
    assert isinstance(error.headers, httpx.Headers)


def test_unknown_http_response_error_custom_message():
    """Test UnknownHTTPResponseError with custom message."""
    custom_message = "Custom error message"
    error = UnknownHTTPResponseError(status=500, message=custom_message)

    assert error.status == 500
    assert str(error) == custom_message


def test_is_api_error_code_comprehensive():
    """Test is_api_error_code with all valid and invalid inputs."""
    for api_code in APIErrorCode:
        assert is_api_error_code(api_code.value), f"Failed for {api_code.value}"

    assert not is_api_error_code("invalid_code")
    assert not is_api_error_code(ClientErrorCode.RequestTimeout.value)
    assert not is_api_error_code(ClientErrorCode.ResponseError.value)
    assert not is_api_error_code(None)
    assert not is_api_error_code(404)
    assert not is_api_error_code([])
    assert not is_api_error_code({})


def test_error_code_enums():
    """Test that error code enums have correct values."""
    assert APIErrorCode.Unauthorized.value == "unauthorized"
    assert APIErrorCode.ObjectNotFound.value == "object_not_found"
    assert APIErrorCode.RateLimited.value == "rate_limited"

    assert ClientErrorCode.RequestTimeout.value == "notionhq_client_request_timeout"
    assert ClientErrorCode.ResponseError.value == "notionhq_client_response_error"


def test_request_timeout_error_custom_message():
    """Test RequestTimeoutError with custom message."""
    custom_message = "Custom timeout message"
    error = RequestTimeoutError(message=custom_message)

    assert str(error) == custom_message
    assert error.code == ClientErrorCode.RequestTimeout


@pytest.mark.asyncio
async def test_request_timeout_error_reject_after_timeout():
    """Test RequestTimeoutError.reject_after_timeout method."""

    async def fast_task():
        await asyncio.sleep(0.01)
        return "success"

    result = await RequestTimeoutError.reject_after_timeout(fast_task(), 1000)
    assert result == "success"

    async def slow_task():
        await asyncio.sleep(2)
        return "should not reach"

    with pytest.raises(RequestTimeoutError):
        await RequestTimeoutError.reject_after_timeout(slow_task(), 100)


def test_parse_api_error_response_body_with_non_string():
    """Test _parse_api_error_response_body with non-string input."""

    result = _parse_api_error_response_body(None)  # type: ignore
    assert result is None

    result = _parse_api_error_response_body(123)  # type: ignore
    assert result is None
