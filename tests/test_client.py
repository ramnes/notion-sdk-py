import base64
import json
import time as time_module
import uuid
from email.utils import formatdate
from typing import Any, Dict, Optional
from unittest.mock import Mock, patch

import httpx
import pytest

from notion_client import APIResponseError, AsyncClient, Client
from notion_client.client import RetryOptions


def _mock_http_response(
    status_code: int,
    code: str = "",
    message: str = "",
    retry_after: Optional[str] = None,
    body: Optional[Dict[str, Any]] = None,
) -> httpx.Response:
    if status_code == 200:
        response_body = body or {}
    else:
        response_body = {"code": code, "message": message, "object": "error"}
        if body:
            response_body.update(body)

    headers: Dict[str, str] = {}
    if retry_after is not None:
        headers["retry-after"] = retry_after

    return httpx.Response(
        status_code=status_code,
        content=json.dumps(response_body).encode(),
        headers=headers,
        request=httpx.Request("GET", "https://api.notion.com/v1/blocks/test"),
    )


def success_response(body: Optional[Dict[str, Any]] = None) -> httpx.Response:
    return _mock_http_response(200, body=body)


def rate_limited_response(retry_after: Optional[str] = None) -> httpx.Response:
    return _mock_http_response(
        429, "rate_limited", "Rate limited", retry_after=retry_after
    )


def internal_server_error_response() -> httpx.Response:
    return _mock_http_response(500, "internal_server_error", "Internal error")


def service_unavailable_response() -> httpx.Response:
    return _mock_http_response(503, "service_unavailable", "Service unavailable")


def validation_error_response() -> httpx.Response:
    return _mock_http_response(400, "validation_error", "Validation failed")


def unauthorized_response() -> httpx.Response:
    return _mock_http_response(401, "unauthorized", "Unauthorized")


def test_client_init(client):
    assert isinstance(client, Client)


def test_async_client_init(async_client):
    assert isinstance(async_client, AsyncClient)


@pytest.mark.vcr()
def test_client_request(client):
    with pytest.raises(APIResponseError):
        client.request("/invalid", "GET")

    response = client.request("/users", "GET")
    assert response["results"]


@pytest.mark.vcr()
async def test_async_client_request(async_client):
    with pytest.raises(APIResponseError):
        await async_client.request("/invalid", "GET")

    response = await async_client.request("/users", "GET")
    assert response["results"]


@pytest.mark.vcr()
def test_client_request_auth(token):
    client = Client(auth="Invalid")

    with pytest.raises(APIResponseError):
        client.request("/users", "GET")

    response = client.request("/users", "GET", auth=token)
    assert response["results"]

    client.close()


@pytest.mark.vcr()
async def test_async_client_request_auth(token):
    async_client = AsyncClient(auth="Invalid")

    with pytest.raises(APIResponseError):
        await async_client.request("/invalid", "GET")

    response = await async_client.request("/users", "GET", auth=token)
    assert response["results"]

    await async_client.aclose()


def test_build_request_with_form_data():
    client = Client()

    form_data = {
        "file": b"file_content",
        "filename": "test.txt",
        "content_type": "text/plain",
    }

    request = client._build_request("POST", "/upload", form_data=form_data)

    assert request.method == "POST"
    assert "/upload" in str(request.url)


def test_build_request_with_file_object():
    """Test _build_request with file-like objects to cover line 130 (tuple case)."""
    client = Client()
    client.client = Mock()

    form_data = {
        "file": ("test.txt", b"content", "text/plain"),
        "name": "document",
    }

    client._build_request("POST", "/upload", form_data=form_data)

    client.client.build_request.assert_called_once()
    call_args = client.client.build_request.call_args

    assert "file" in call_args[1]["files"]
    assert "name" in call_args[1]["data"]


def test_build_request_with_read_object():
    """Test _build_request with objects having read method to cover line 132."""
    client = Client()
    client.client = Mock()

    class MockFile:
        def read(self):
            return b"test content"

    file_obj = MockFile()

    form_data = {
        "document": file_obj,
        "title": "test document",
    }

    client._build_request("POST", "/upload", form_data=form_data)

    client.client.build_request.assert_called_once()
    call_args = client.client.build_request.call_args

    assert "document" in call_args[1]["files"]
    assert "title" in call_args[1]["data"]


def test_build_request_with_auth():
    """Test _build_request with auth parameter to cover line 113."""
    client = Client()

    request = client._build_request("POST", "/test", auth="test_token")

    assert request.method == "POST"
    assert "/test" in str(request.url)


def test_parse_response_with_json_decode_error_in_error_response():
    """Test that JSON decode errors in error responses are handled properly."""
    client = Client()

    error_response = Mock(spec=httpx.Response)
    error_response.json.side_effect = json.JSONDecodeError("test", "doc", 0)
    error_response.status_code = 500
    error_response.text = "Internal Server Error"
    error_response.headers = {}

    http_error = httpx.HTTPStatusError(
        "500 Server Error", request=Mock(), response=error_response
    )

    mock_response = Mock(spec=httpx.Response)
    mock_response.raise_for_status.side_effect = http_error

    from notion_client.errors import HTTPResponseError

    with pytest.raises(HTTPResponseError):
        client._parse_response(mock_response)


def test_client_context_manager():
    """Test client context manager methods."""
    with Client() as client:
        assert isinstance(client, Client)


def test_client_close():
    """Test client close method."""
    client = Client()
    client.close()


def test_client_request_timeout():
    client = Client()

    with patch.object(
        client.client, "send", side_effect=httpx.TimeoutException("Timeout")
    ):
        from notion_client.errors import RequestTimeoutError

        with pytest.raises(RequestTimeoutError):
            client.request("/test", "GET")


async def test_async_client_request_timeout():
    async_client = AsyncClient()

    with patch.object(
        async_client.client, "send", side_effect=httpx.TimeoutException("Timeout")
    ):
        from notion_client.errors import RequestTimeoutError

        with pytest.raises(RequestTimeoutError):
            await async_client.request("/test", "GET")


def test_request_with_dict_auth(client):
    """Test that dict auth produces a Basic Auth Authorization header."""
    auth_dict = {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
    }

    mock_response = Mock(spec=httpx.Response)
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"object": "token"}

    with patch.object(client.client, "send", return_value=mock_response) as mock_send:
        client.request("/oauth/token", "POST", auth=auth_dict)

    captured_request = mock_send.call_args.args[0]

    expected_credentials = "test_client_id:test_client_secret"
    expected_encoded = base64.b64encode(expected_credentials.encode()).decode()

    assert captured_request.headers["Authorization"] == f"Basic {expected_encoded}"


def test_request_logs_success_without_request_id(client):
    """Test that a successful response without request_id is logged correctly."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"results": []}

    with patch.object(client.client, "send", return_value=mock_response):
        with patch.object(client.logger, "info") as mock_info:
            client.request("/users", "GET")

            mock_info.assert_called_with("request success: method=GET, path=/users")


def test_request_propagates_non_notion_error(client):
    """Test that non-Notion errors raised during request propagate to the caller."""
    with patch.object(
        client.client, "send", side_effect=ValueError("unexpected error")
    ):
        with pytest.raises(ValueError, match="unexpected error"):
            client.request("/test", "GET")


async def test_async_request_propagates_non_notion_error(async_client):
    """Test that non-Notion errors raised during async request propagate to the caller."""
    with patch.object(
        async_client.client, "send", side_effect=ValueError("unexpected error")
    ):
        with pytest.raises(ValueError, match="unexpected error"):
            await async_client.request("/test", "GET")


@patch("time.sleep", return_value=None)
def test_retries_on_rate_limit_and_succeeds(mock_sleep):
    client = Client(retry=RetryOptions(max_retries=2))
    responses = [rate_limited_response(retry_after="5"), success_response()]
    with patch.object(client.client, "send", side_effect=responses):
        assert client.request("blocks/test", "GET") == {}
        assert client.client.send.call_count == 2


@patch("time.sleep", return_value=None)
def test_does_not_retry_when_disabled(mock_sleep):
    client = Client(retry=False)
    with patch.object(client.client, "send", return_value=rate_limited_response()):
        with pytest.raises(APIResponseError):
            client.request("blocks/test", "GET")
        assert client.client.send.call_count == 1


@patch("time.sleep", return_value=None)
def test_retries_on_internal_server_error(mock_sleep):
    client = Client(retry=RetryOptions(max_retries=2, initial_retry_delay_ms=1000))
    responses = [internal_server_error_response(), success_response()]
    with patch.object(client.client, "send", side_effect=responses):
        assert client.request("blocks/test", "GET") == {}
        assert client.client.send.call_count == 2


@patch("time.sleep", return_value=None)
def test_retries_on_service_unavailable(mock_sleep):
    client = Client(retry=RetryOptions(max_retries=2, initial_retry_delay_ms=1000))
    responses = [service_unavailable_response(), success_response()]
    with patch.object(client.client, "send", side_effect=responses):
        assert client.request("blocks/test", "GET") == {}
        assert client.client.send.call_count == 2


@patch("time.sleep", return_value=None)
def test_does_not_retry_on_validation_error(mock_sleep):
    client = Client(retry=RetryOptions(max_retries=2))
    with patch.object(client.client, "send", return_value=validation_error_response()):
        with pytest.raises(APIResponseError):
            client.request("blocks/test", "GET")
        assert client.client.send.call_count == 1


@patch("time.sleep", return_value=None)
def test_does_not_retry_on_unauthorized(mock_sleep):
    client = Client(retry=RetryOptions(max_retries=2))
    with patch.object(client.client, "send", return_value=unauthorized_response()):
        with pytest.raises(APIResponseError):
            client.request("blocks/test", "GET")
        assert client.client.send.call_count == 1


@patch("time.sleep", return_value=None)
def test_respects_max_retries_limit(mock_sleep):
    client = Client(retry=RetryOptions(max_retries=3))
    with patch.object(
        client.client, "send", return_value=rate_limited_response(retry_after="1")
    ):
        with pytest.raises(APIResponseError):
            client.request("blocks/test", "GET")
        assert client.client.send.call_count == 4  # 1 initial + 3 retries


@patch("time.sleep", return_value=None)
def test_uses_default_retry_settings(mock_sleep):
    """Default max_retries=2: 1 initial + 2 retries = 3 calls."""
    client = Client()
    responses = [
        rate_limited_response(retry_after="1"),
        rate_limited_response(retry_after="1"),
        success_response(),
    ]
    with patch.object(client.client, "send", side_effect=responses):
        assert client.request("blocks/test", "GET") == {}
        assert client.client.send.call_count == 3


@patch("time.sleep", return_value=None)
def test_uses_default_retry_when_retry_is_true(mock_sleep):
    """retry=True falls back to default RetryOptions (max_retries=2)."""
    client = Client(retry=True)
    responses = [
        rate_limited_response(retry_after="1"),
        rate_limited_response(retry_after="1"),
        success_response(),
    ]
    with patch.object(client.client, "send", side_effect=responses):
        assert client.request("blocks/test", "GET") == {}
        assert client.client.send.call_count == 3


@patch("time.sleep", return_value=None)
def test_respects_retry_after_delta_seconds(mock_sleep):
    client = Client(retry=RetryOptions(max_retries=1))
    responses = [rate_limited_response(retry_after="10"), success_response()]
    with patch.object(client.client, "send", side_effect=responses):
        client.request("blocks/test", "GET")
        assert client.client.send.call_count == 2
        mock_sleep.assert_called_once()
        assert mock_sleep.call_args[0][0] == 10.0


@patch("time.sleep", return_value=None)
def test_respects_retry_after_http_date(mock_sleep):
    http_date = formatdate(time_module.time() + 3, usegmt=True)
    client = Client(retry=RetryOptions(max_retries=1))
    responses = [rate_limited_response(retry_after=http_date), success_response()]
    with patch.object(client.client, "send", side_effect=responses):
        client.request("blocks/test", "GET")
        assert client.client.send.call_count == 2
        mock_sleep.assert_called_once()
        assert mock_sleep.call_args[0][0] > 0


@patch("time.sleep", return_value=None)
def test_falls_back_to_backoff_when_retry_after_invalid(mock_sleep):
    client = Client(retry=RetryOptions(max_retries=1, initial_retry_delay_ms=1000))
    responses = [rate_limited_response(retry_after="invalid"), success_response()]
    with patch.object(client.client, "send", side_effect=responses):
        client.request("blocks/test", "GET")
        assert client.client.send.call_count == 2


@patch("time.sleep", return_value=None)
def test_uses_exponential_backoff_when_no_retry_after(mock_sleep):
    client = Client(retry=RetryOptions(max_retries=1, initial_retry_delay_ms=1000))
    responses = [rate_limited_response(), success_response()]
    with patch.object(client.client, "send", side_effect=responses):
        client.request("blocks/test", "GET")
        assert client.client.send.call_count == 2
        mock_sleep.assert_called_once()


@patch("time.sleep", return_value=None)
def test_ignores_negative_retry_after(mock_sleep):
    client = Client(retry=RetryOptions(max_retries=1, initial_retry_delay_ms=1000))
    responses = [rate_limited_response(retry_after="-5"), success_response()]
    with patch.object(client.client, "send", side_effect=responses):
        client.request("blocks/test", "GET")
        assert client.client.send.call_count == 2


@patch("time.sleep", return_value=None)
def test_caps_retry_delay_at_max(mock_sleep):
    client = Client(retry=RetryOptions(max_retries=1, max_retry_delay_ms=5000))
    responses = [rate_limited_response(retry_after="300"), success_response()]
    with patch.object(client.client, "send", side_effect=responses):
        client.request("blocks/test", "GET")
        assert client.client.send.call_count == 2
        mock_sleep.assert_called_once()
        assert mock_sleep.call_args[0][0] == 5.0


@patch("time.sleep", return_value=None)
def test_does_not_retry_post_on_internal_server_error(mock_sleep):
    client = Client(retry=RetryOptions(max_retries=2, initial_retry_delay_ms=1000))
    with patch.object(
        client.client, "send", return_value=internal_server_error_response()
    ):
        with pytest.raises(APIResponseError):
            client.request(
                "pages", "POST", body={"parent": {"page_id": str(uuid.uuid4())}}
            )
        assert client.client.send.call_count == 1


@patch("time.sleep", return_value=None)
def test_does_not_retry_post_on_service_unavailable(mock_sleep):
    client = Client(retry=RetryOptions(max_retries=2, initial_retry_delay_ms=1000))
    with patch.object(
        client.client, "send", return_value=service_unavailable_response()
    ):
        with pytest.raises(APIResponseError):
            client.request(
                "pages", "POST", body={"parent": {"page_id": str(uuid.uuid4())}}
            )
        assert client.client.send.call_count == 1


@patch("time.sleep", return_value=None)
def test_does_not_retry_patch_on_internal_server_error(mock_sleep):
    client = Client(retry=RetryOptions(max_retries=2, initial_retry_delay_ms=1000))
    with patch.object(
        client.client, "send", return_value=internal_server_error_response()
    ):
        with pytest.raises(APIResponseError):
            client.request(
                f"pages/{str(uuid.uuid4())}", "PATCH", body={"properties": {}}
            )
        assert client.client.send.call_count == 1


@patch("time.sleep", return_value=None)
def test_retries_post_on_rate_limit(mock_sleep):
    client = Client(retry=RetryOptions(max_retries=2, initial_retry_delay_ms=1000))
    responses = [rate_limited_response(retry_after="1"), success_response()]
    with patch.object(client.client, "send", side_effect=responses):
        result = client.request(
            "pages", "POST", body={"parent": {"page_id": str(uuid.uuid4())}}
        )
        assert result == {}
        assert client.client.send.call_count == 2


@patch("time.sleep", return_value=None)
def test_retries_delete_on_internal_server_error(mock_sleep):
    client = Client(retry=RetryOptions(max_retries=2, initial_retry_delay_ms=1000))
    responses = [internal_server_error_response(), success_response()]
    with patch.object(client.client, "send", side_effect=responses):
        assert client.request(f"blocks/{str(uuid.uuid4())}", "DELETE") == {}
        assert client.client.send.call_count == 2


@patch("time.sleep", return_value=None)
def test_retries_delete_on_service_unavailable(mock_sleep):
    client = Client(retry=RetryOptions(max_retries=2, initial_retry_delay_ms=1000))
    responses = [service_unavailable_response(), success_response()]
    with patch.object(client.client, "send", side_effect=responses):
        assert client.request(f"blocks/{str(uuid.uuid4())}", "DELETE") == {}
        assert client.client.send.call_count == 2


@patch("time.sleep", return_value=None)
def test_retries_get_on_internal_server_error(mock_sleep):
    client = Client(retry=RetryOptions(max_retries=2, initial_retry_delay_ms=1000))
    responses = [internal_server_error_response(), success_response()]
    with patch.object(client.client, "send", side_effect=responses):
        assert client.request(f"blocks/{str(uuid.uuid4())}", "GET") == {}
        assert client.client.send.call_count == 2


@patch("asyncio.sleep", return_value=None)
async def test_async_retries_on_rate_limit_and_succeeds(mock_sleep):
    client = AsyncClient(retry=RetryOptions(max_retries=2))
    responses = [rate_limited_response(retry_after="5"), success_response()]
    with patch.object(client.client, "send", side_effect=responses):
        assert await client.request("blocks/test", "GET") == {}
        assert client.client.send.call_count == 2


@patch("asyncio.sleep", return_value=None)
async def test_async_does_not_retry_when_disabled(mock_sleep):
    client = AsyncClient(retry=False)
    with patch.object(client.client, "send", return_value=rate_limited_response()):
        with pytest.raises(APIResponseError):
            await client.request("blocks/test", "GET")
        assert client.client.send.call_count == 1


@patch("asyncio.sleep", return_value=None)
async def test_async_retries_on_internal_server_error(mock_sleep):
    client = AsyncClient(retry=RetryOptions(max_retries=2, initial_retry_delay_ms=1000))
    responses = [internal_server_error_response(), success_response()]
    with patch.object(client.client, "send", side_effect=responses):
        assert await client.request("blocks/test", "GET") == {}
        assert client.client.send.call_count == 2


@patch("asyncio.sleep", return_value=None)
async def test_async_does_not_retry_post_on_server_error(mock_sleep):
    client = AsyncClient(retry=RetryOptions(max_retries=2, initial_retry_delay_ms=1000))
    with patch.object(
        client.client, "send", return_value=internal_server_error_response()
    ):
        with pytest.raises(APIResponseError):
            await client.request(
                "pages", "POST", body={"parent": {"page_id": str(uuid.uuid4())}}
            )
        assert client.client.send.call_count == 1


@patch("asyncio.sleep", return_value=None)
async def test_async_respects_max_retries(mock_sleep):
    client = AsyncClient(retry=RetryOptions(max_retries=3))
    with patch.object(
        client.client, "send", return_value=rate_limited_response(retry_after="1")
    ):
        with pytest.raises(APIResponseError):
            await client.request("blocks/test", "GET")
        assert client.client.send.call_count == 4  # 1 initial + 3 retries
