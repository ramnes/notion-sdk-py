from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Union

import httpx


class RequestTimeoutError(Exception):
    code = "notionhq_client_request_timeout"

    def __init__(self, message: str = "Request to Notion API has timed out") -> None:
        super().__init__(message)
        self.name = "RequestTimeoutError"

    @staticmethod
    def is_request_timeout_error(e: Exception) -> bool:
        return (
            isinstance(e, RequestTimeoutError)
            and hasattr(e, "code")
            and e.code == RequestTimeoutError.code
        )


class HTTPResponseError(Exception):
    code: str = "notionhq_client_response_error"
    status: int
    headers: httpx.Headers
    body: str

    def __init__(self, response: httpx.Response, message: Optional[str] = None) -> None:
        super().__init__(
            message
            or f"Request to Notion API failed with status: {response.status_code}"
        )
        self.status = response.status_code
        self.headers = response.headers
        self.body = response.text

    def is_http_response_error(e: Exception) -> bool:
        return (
            isinstance(e, HTTPResponseError)
            and hasattr(e, "code")
            and e.code == HTTPResponseError.code
        )


class APIErrorCode(str, Enum):
    Unauthorized = "unauthorized"
    RestrictedResource = "restricted_resource"
    ObjectNotFound = "object_not_found"
    RateLimited = "rate_limited"
    InvalidJSON = "invalid_json"
    InvalidRequestURL = "invalid_request_url"
    InvalidRequest = "invalid_request"
    ValidationError = "validation_error"
    ConflictError = "conflict_error"
    InternalServerError = "internal_server_error"
    ServiceUnavailable = "service_unavailable"


@dataclass
class APIErrorResponseBody:
    code: APIErrorCode
    message: str


class APIResponseError(HTTPResponseError):
    code: APIErrorCode

    def __init__(self, response: httpx.Response, body: APIErrorResponseBody) -> None:
        super().__init__(response, body.message)
        self.code = body.code

    @staticmethod
    def is_api_response_error(e: Exception) -> bool:
        return (
            isinstance(e, APIResponseError)
            and hasattr(e, "code")
            and is_api_error_code(e.code)
        )


def build_request_error(
    e: Exception,
) -> Union[RequestTimeoutError, APIResponseError, HTTPResponseError, None]:
    if is_timeout_error(e):
        return RequestTimeoutError()
    if is_http_error(e):
        api_error_response_body = parse_api_error_response_body(e.response.json())
        if api_error_response_body is not None:
            return APIResponseError(e.response, api_error_response_body)
        return HTTPResponseError(e.response)
    return None


def parse_api_error_response_body(
    body: Dict[Any, Any]
) -> Union[APIErrorResponseBody, None]:
    if not is_api_error_code(body["code"]):
        return None

    return APIErrorResponseBody(code=body["code"], message=body["message"])


# Type Guards


def is_api_error_code(code: str) -> bool:
    codes = [error_code.value for error_code in APIErrorCode]
    return type(code) == str and code in codes


def is_timeout_error(e: Exception) -> bool:
    return (
        isinstance(e, httpx.TimeoutException)
        and hasattr(e, "request")
        and isinstance(e.request, httpx.Request)
    )


def is_http_error(e: Exception) -> bool:
    return (
        isinstance(e, httpx.HTTPStatusError)
        and hasattr(e, "request")
        and hasattr(e, "response")
        and isinstance(e.request, httpx.Request)
        and isinstance(e.response, httpx.Response)
    )
