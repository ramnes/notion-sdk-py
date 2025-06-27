import pytest
import json
import gzip
from unittest.mock import Mock, patch

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


def test_extract_json_from_response_with_gzip():
    client = Client()

    json_data = {"message": "test", "status": "ok"}
    json_str = json.dumps(json_data)
    gzip_content = gzip.compress(json_str.encode("utf-8"))

    mock_response = Mock(spec=httpx.Response)
    mock_response.content = gzip_content
    mock_response.json.side_effect = json.JSONDecodeError("test", "doc", 0)

    result = client._extract_json_from_response(mock_response)
    assert result == json_data


def test_extract_json_from_response_with_bad_gzip():
    client = Client()

    bad_gzip_content = b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\xff" + b"invalid_data"

    mock_response = Mock(spec=httpx.Response)
    mock_response.content = bad_gzip_content
    mock_response.json.side_effect = json.JSONDecodeError("test", "doc", 0)
    mock_response.headers = {"content-type": "application/json", "content-encoding": "gzip"}

    with patch.object(client, "logger") as mock_logger:
        with patch('gzip.decompress', side_effect=gzip.BadGzipFile("Invalid gzip file")):
            with pytest.raises(json.JSONDecodeError):
                client._extract_json_from_response(mock_response)

            mock_logger.error.assert_called()
            mock_logger.debug.assert_called()

            error_calls = [call[0][0] for call in mock_logger.error.call_args_list]
            debug_calls = [call[0][0] for call in mock_logger.debug.call_args_list]

            assert any("Failed to decompress gzip response" in call for call in error_calls)
            assert any("Response headers" in call for call in debug_calls)
            assert any("Response content type" in call for call in debug_calls)
            assert any("Response content encoding" in call for call in debug_calls)
            assert any("Content starts with" in call for call in debug_calls)
        assert any("Content starts with" in call for call in debug_calls)


def test_extract_json_from_response_with_non_gzip_decode_error():
    client = Client()

    invalid_content = b"invalid json content"

    mock_response = Mock(spec=httpx.Response)
    mock_response.content = invalid_content
    mock_response.json.side_effect = json.JSONDecodeError("test", "doc", 0)

    with patch.object(client, "logger") as mock_logger:
        with pytest.raises(json.JSONDecodeError):
            client._extract_json_from_response(mock_response)

        mock_logger.error.assert_called()
        mock_logger.debug.assert_called()

        error_calls = [call[0][0] for call in mock_logger.error.call_args_list]
        debug_calls = [call[0][0] for call in mock_logger.debug.call_args_list]

        assert any("JSON decode error" in call for call in error_calls)
        assert any("Response content" in call for call in debug_calls)


def test_build_request_with_form_data():
    client = Client()

    form_data = {
        "file": b"file_content",
        "filename": "test.txt",
        "content_type": "text/plain"
    }

    request = client._build_request("POST", "/upload", form_data=form_data)

    assert request.method == "POST"
    assert "/upload" in str(request.url)


def test_parse_response_with_http_error_and_json_decode_error():
    client = Client()

    error_response = Mock(spec=httpx.Response)
    error_response.status_code = 500
    error_response.text = "Internal Server Error"
    error_response.content = b"invalid json content"
    error_response.headers = {}
    error_response.json.side_effect = json.JSONDecodeError("test", "doc", 0)

    http_error = httpx.HTTPStatusError("500 Server Error", request=Mock(), response=error_response)

    mock_response = Mock(spec=httpx.Response)
    mock_response.raise_for_status.side_effect = http_error

    with patch.object(client, 'logger') as mock_logger:
        from notion_client.errors import HTTPResponseError
        with pytest.raises(HTTPResponseError):
            client._parse_response(mock_response)

        mock_logger.error.assert_called()


def test_parse_response_with_non_api_error_code():
    client = Client()

    error_response = Mock(spec=httpx.Response)
    error_response.status_code = 500
    error_response.text = "Internal Server Error"
    error_response.headers = {}
    error_response.json.return_value = {"message": "Server error", "code": "unknown_error"}

    http_error = httpx.HTTPStatusError("500 Server Error", request=Mock(), response=error_response)

    mock_response = Mock(spec=httpx.Response)
    mock_response.raise_for_status.side_effect = http_error

    with patch.object(client, '_extract_json_from_response', return_value={"message": "Server error", "code": "unknown_error"}):
        with patch('notion_client.errors.is_api_error_code', return_value=False):
            from notion_client.errors import HTTPResponseError
            with pytest.raises(HTTPResponseError):
                client._parse_response(mock_response)


def test_client_request_timeout():
    client = Client()

    with patch.object(client.client, 'send', side_effect=httpx.TimeoutException("Timeout")):
        from notion_client.errors import RequestTimeoutError
        with pytest.raises(RequestTimeoutError):
            client.request("/test", "GET")


async def test_async_client_request_timeout():
    async_client = AsyncClient()

    with patch.object(async_client.client, 'send', side_effect=httpx.TimeoutException("Timeout")):
        from notion_client.errors import RequestTimeoutError
        with pytest.raises(RequestTimeoutError):
            await async_client.request("/test", "GET")
