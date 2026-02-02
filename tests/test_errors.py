import pytest
from httpx import TimeoutException
import httpx
import asyncio

from notion_client.errors import (
    APIErrorCode,
    ClientErrorCode,
    is_notion_client_error,
    RequestTimeoutError,
    InvalidPathParameterError,
    validate_request_path,
    HTTPResponseError,
    is_http_response_error,
    UnknownHTTPResponseError,
    APIResponseError,
    build_request_error,
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

    response = httpx.Response(
        status_code=400,
        headers=httpx.Headers(),
        content=b"Error",
    )
    error = build_request_error(response, None)  # type: ignore
    assert isinstance(error, UnknownHTTPResponseError)

    error = build_request_error(response, 123)  # type: ignore
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


def test_error_code_enums():
    """Test that error code enums have correct values."""
    assert APIErrorCode.Unauthorized.value == "unauthorized"
    assert APIErrorCode.ObjectNotFound.value == "object_not_found"
    assert APIErrorCode.RateLimited.value == "rate_limited"

    assert ClientErrorCode.RequestTimeout.value == "notionhq_client_request_timeout"
    assert ClientErrorCode.ResponseError.value == "notionhq_client_response_error"
    assert (
        ClientErrorCode.InvalidPathParameter.value
        == "notionhq_client_invalid_path_parameter"
    )


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


def test_invalid_path_parameter_error():
    """Test InvalidPathParameterError class."""
    error = InvalidPathParameterError()
    assert error.code == ClientErrorCode.InvalidPathParameter
    assert "invalid characters" in str(error)

    custom_message = "Custom path error message"
    error = InvalidPathParameterError(message=custom_message)
    assert str(error) == custom_message


def test_invalid_path_parameter_error_static_method():
    """Test InvalidPathParameterError.is_invalid_path_parameter_error static method."""
    path_error = InvalidPathParameterError()
    assert InvalidPathParameterError.is_invalid_path_parameter_error(path_error)

    timeout_error = RequestTimeoutError()
    assert not InvalidPathParameterError.is_invalid_path_parameter_error(timeout_error)

    unknown_error = UnknownHTTPResponseError(status=500)
    assert not InvalidPathParameterError.is_invalid_path_parameter_error(unknown_error)

    api_error = APIResponseError(
        code=APIErrorCode.ObjectNotFound,
        status=404,
        message="Not found",
        headers=httpx.Headers(),
        raw_body_text="{}",
    )
    assert not InvalidPathParameterError.is_invalid_path_parameter_error(api_error)

    assert not InvalidPathParameterError.is_invalid_path_parameter_error(None)
    assert not InvalidPathParameterError.is_invalid_path_parameter_error("error")


def test_is_notion_client_error_with_invalid_path_parameter_error():
    """Test is_notion_client_error recognizes InvalidPathParameterError."""
    path_error = InvalidPathParameterError()
    assert is_notion_client_error(path_error)


def test_validate_request_path_allows_valid_paths():
    """Test validate_request_path allows valid paths."""
    # Valid UUID
    validate_request_path("blocks/9f96555b-cf98-4889-83b0-bd6bbe53911e")
    # Simple API paths
    validate_request_path("v1/users")
    validate_request_path("databases")


def test_validate_request_path_rejects_literal_path_traversal():
    """Test validate_request_path rejects literal '..' sequences."""
    with pytest.raises(InvalidPathParameterError) as exc_info:
        validate_request_path("../databases/xyz")
    assert ".." in str(exc_info.value)
    assert "../databases/xyz" in str(exc_info.value)

    with pytest.raises(InvalidPathParameterError):
        validate_request_path("blocks/../databases/xyz")

    with pytest.raises(InvalidPathParameterError):
        validate_request_path("foo/../bar")

    with pytest.raises(InvalidPathParameterError):
        validate_request_path("path/to/../../secret")


def test_validate_request_path_rejects_encoded_path_traversal():
    """Test validate_request_path rejects URL-encoded '..' sequences."""
    # Lowercase %2e%2e
    with pytest.raises(InvalidPathParameterError) as exc_info:
        validate_request_path("%2e%2e/databases/xyz")
    assert "encoded" in str(exc_info.value).lower()

    # Uppercase %2E%2E
    with pytest.raises(InvalidPathParameterError):
        validate_request_path("%2E%2E/databases/xyz")

    # Mixed case %2E%2e
    with pytest.raises(InvalidPathParameterError):
        validate_request_path("%2E%2e/databases/xyz")

    # Fully encoded path traversal %2e%2e%2f
    with pytest.raises(InvalidPathParameterError):
        validate_request_path("%2e%2e%2fdatabases/xyz")


def test_validate_request_path_handles_invalid_percent_encoding():
    """Test validate_request_path handles invalid percent encoding gracefully."""
    # Invalid percent encoding should not raise (not a traversal concern)
    # Python's unquote preserves invalid sequences unlike JS's decodeURIComponent
    validate_request_path("%2einvalid%2e%ZZ")
    validate_request_path("path%2ewith%invalid")
