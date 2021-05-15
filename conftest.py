from enum import Enum

import httpx
import pytest

from notion_client.errors import APIErrorCode

PROPER_AUTH = "proper_auth"


class StatusCode(Enum):
    Ok = 200
    BadRequest = 400
    Unauthorized = 401
    Forbidden = 403
    NotFound = 404
    Conflict = 409
    TooManyRequest = 429
    InternalServerError = 500
    ServiceUnavailable = 503


class MockResponse(httpx.Response):
    def __init__(
        self, request: httpx.Request, code: APIErrorCode = None, json: dict = None
    ):
        if code in [
            APIErrorCode.InvalidJSON,
            APIErrorCode.InvalidRequestURL,
            APIErrorCode.InvalidRequest,
            APIErrorCode.ValidationError,
        ]:
            status_code = StatusCode.BadRequest.value
        elif code == APIErrorCode.Unauthorized:
            status_code = StatusCode.Unauthorized.value
        elif code == APIErrorCode.RestrictedResource:
            status_code = StatusCode.Forbidden.value
        elif code == APIErrorCode.ObjectNotFound:
            status_code = StatusCode.NotFound.value
        elif code == APIErrorCode.ConflictError:
            status_code = StatusCode.Conflict.value
        elif code == APIErrorCode.RateLimited:
            status_code = StatusCode.TooManyRequest.value
        elif code == APIErrorCode.InternalServerError:
            status_code = StatusCode.InternalServerError.value
        elif code == APIErrorCode.ServiceUnavailable:
            status_code = StatusCode.ServiceUnavailable.value
        else:
            status_code = StatusCode.Ok.value
        super().__init__(
            request=request,
            status_code=status_code,
            json=json or {"code": code.value, "message": ""},
        )


@pytest.fixture(autouse=True)
def mock_httpx(monkeypatch):
    original_send = httpx.Client.send

    def mock_send(self, request: httpx.Request):
        if request.headers.get("Authorization") != f"Bearer {PROPER_AUTH}":
            return MockResponse(request=request, code=APIErrorCode.Unauthorized)
        else:
            return MockResponse(request=request, json={"foo": "bar"})
        return original_send(self, request)

    monkeypatch.setattr(httpx.Client, "send", mock_send)
