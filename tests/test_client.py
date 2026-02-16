import pytest
import json
from unittest.mock import Mock, patch
import base64
from notion_client import APIResponseError, AsyncClient, Client
import httpx


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


def test_build_request_with_dict_auth(client):
    """Test _build_request with public integration auth"""

    auth_dict = {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
    }

    request = client._build_request("POST", "/oauth/token", auth=auth_dict)

    expected_credentials = "test_client_id:test_client_secret"
    expected_encoded = base64.b64encode(expected_credentials.encode()).decode()

    assert request.headers["Authorization"] == f"Basic {expected_encoded}"


def test_log_request_success_without_request_id(client):
    """Test _log_request_success when response has no request_id."""
    response_body = {"results": []}

    with patch.object(client.logger, "info") as mock_info:
        client._log_request_success("GET", "/users", response_body)

        mock_info.assert_called_once_with("request success: method=GET, path=/users")


def test_log_request_error_with_non_notion_error(client):
    """Test _handle_request_error with non-notion error."""

    generic_error = ValueError("Some generic error")

    with pytest.raises(ValueError, match="Some generic error"):
        client._log_request_error(generic_error)
