"""Custom exceptions for notion-sdk-py.

This module defines the exceptions that can be raised when an error occurs.
"""

import asyncio
import json
from enum import Enum
from typing import Any, Dict, Optional, Union, Set
import sys
import httpx
from urllib.parse import unquote

if sys.version_info >= (3, 10):
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard  # pragma: no cover


class APIErrorCode(str, Enum):
    """Error codes returned in responses from the API."""

    Unauthorized = "unauthorized"
    """The bearer token is not valid."""

    RestrictedResource = "restricted_resource"
    """Given the bearer token used, the client doesn't have permission to
    perform this operation."""

    ObjectNotFound = "object_not_found"
    """Given the bearer token used, the resource does not exist.
    This error can also indicate that the resource has not been shared with owner
    of the bearer token."""

    RateLimited = "rate_limited"
    """This request exceeds the number of requests allowed. Slow down and try again."""

    InvalidJSON = "invalid_json"
    """The request body could not be decoded as JSON."""

    InvalidRequestURL = "invalid_request_url"
    """The request URL is not valid."""

    InvalidRequest = "invalid_request"
    """This request is not supported."""

    ValidationError = "validation_error"
    """The request body does not match the schema for the expected parameters."""

    ConflictError = "conflict_error"
    """The transaction could not be completed, potentially due to a data collision.
    Make sure the parameters are up to date and try again."""

    InternalServerError = "internal_server_error"
    """An unexpected error occurred. Reach out to Notion support."""

    ServiceUnavailable = "service_unavailable"
    """Notion is unavailable. Try again later.
    This can occur when the time to respond to a request takes longer than 60 seconds,
    the maximum request timeout."""

    GatewayTimeout = "gateway_timeout"
    """The request timed out on the server side."""


class ClientErrorCode(str, Enum):
    """Error codes generated for client errors."""

    RequestTimeout = "notionhq_client_request_timeout"
    ResponseError = "notionhq_client_response_error"
    InvalidPathParameter = "notionhq_client_invalid_path_parameter"


# Error codes on errors thrown by the `Client`.
NotionErrorCode = Union[APIErrorCode, ClientErrorCode]


class NotionClientErrorBase(Exception):
    """Base error type for all Notion client errors."""

    code: Union[str, NotionErrorCode]

    def __init__(self, message: str = "") -> None:
        super().__init__(message)


def is_notion_client_error(error: Any) -> TypeGuard["NotionClientError"]:
    return isinstance(error, NotionClientErrorBase)


def _is_notion_client_error_with_code(error: Any, codes: Set[str]) -> bool:
    if not is_notion_client_error(error):
        return False
    error_code = error.code
    if isinstance(error_code, Enum):
        error_code = error_code.value

    return error_code in codes


class RequestTimeoutError(NotionClientErrorBase):
    """Error thrown by the client if a request times out."""

    code: ClientErrorCode = ClientErrorCode.RequestTimeout

    def __init__(self, message: str = "Request to Notion API has timed out") -> None:
        super().__init__(message)

    @staticmethod
    def is_request_timeout_error(error: Any) -> bool:
        return _is_notion_client_error_with_code(
            error,
            {ClientErrorCode.RequestTimeout.value},
        )

    @staticmethod
    async def reject_after_timeout(coro: Any, timeout_ms: int) -> Any:
        try:
            return await asyncio.wait_for(coro, timeout=timeout_ms / 1000.0)
        except asyncio.TimeoutError:
            raise RequestTimeoutError()


class InvalidPathParameterError(NotionClientErrorBase):
    """Error thrown when a path parameter contains invalid characters such as
    path traversal sequences (..) that could alter the intended API endpoint."""

    code: ClientErrorCode = ClientErrorCode.InvalidPathParameter

    def __init__(
        self,
        message: str = (
            "Path parameter contains invalid characters that could alter the request path"
        ),
    ) -> None:
        super().__init__(message)

    @staticmethod
    def is_invalid_path_parameter_error(error: object) -> bool:
        return _is_notion_client_error_with_code(
            error,
            {ClientErrorCode.InvalidPathParameter.value},
        )


def validate_request_path(path: str) -> None:
    """Validates that a request path does not contain path traversal sequences.
    Raises InvalidPathParameterError if the path contains ".." segments,
    including URL-encoded variants like %2e%2e."""

    # Check for literal path traversal
    if ".." in path:
        raise InvalidPathParameterError(
            f'Request path "{path}" contains path traversal sequence ".."'
        )

    # Check for URL-encoded path traversal (%2e = '.')
    # Only decode if path contains potential encoded dots
    if "%2e" in path.lower():
        decoded = unquote(path)
        if ".." in decoded:
            raise InvalidPathParameterError(
                f'Request path "{path}" contains encoded path traversal sequence'
            )


HTTPResponseErrorCode = Union[ClientErrorCode, APIErrorCode]


def _get_response_header(headers: httpx.Headers, name: str) -> Optional[str]:
    """Reads a response header by name, or returns None when it is absent.

    Header names are case-insensitive per RFC 9110, which `httpx.Headers`
    already honors, so this only narrows the value to an optional string.
    """
    value = headers.get(name)
    return value if isinstance(value, str) else None


class HTTPResponseError(NotionClientErrorBase):
    code: Union[str, APIErrorCode]
    status: int
    headers: httpx.Headers
    body: str
    additional_data: Optional[Dict[str, Any]]
    request_id: Optional[str]
    ray_id: Optional[str]  # Value of the `cf-ray` response header, when present.

    def __init__(
        self,
        code: Union[str, APIErrorCode],
        status: int,
        message: str,
        headers: httpx.Headers,
        raw_body_text: str,
        additional_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status = status
        self.headers = headers
        self.body = raw_body_text
        self.additional_data = additional_data
        self.request_id = request_id or _get_response_header(
            self.headers, "x-notion-request-id"
        )
        self.ray_id = _get_response_header(self.headers, "cf-ray")


_http_response_error_codes: Set[str] = {
    ClientErrorCode.ResponseError.value,
    APIErrorCode.Unauthorized.value,
    APIErrorCode.RestrictedResource.value,
    APIErrorCode.ObjectNotFound.value,
    APIErrorCode.RateLimited.value,
    APIErrorCode.InvalidJSON.value,
    APIErrorCode.InvalidRequestURL.value,
    APIErrorCode.InvalidRequest.value,
    APIErrorCode.ValidationError.value,
    APIErrorCode.ConflictError.value,
    APIErrorCode.InternalServerError.value,
    APIErrorCode.ServiceUnavailable.value,
    APIErrorCode.GatewayTimeout.value,
}


def is_http_response_error(error: Any) -> TypeGuard[HTTPResponseError]:
    return _is_notion_client_error_with_code(error, _http_response_error_codes)


class UnknownHTTPResponseError(HTTPResponseError):
    """Error thrown if an API call responds with an unknown error code, or does not respond with
    a properly-formatted error.
    """

    def __init__(
        self,
        status: int,
        message: Optional[str] = None,
        headers: Optional[httpx.Headers] = None,
        raw_body_text: str = "",
    ) -> None:
        if headers is None:
            headers = httpx.Headers()
        if message is None:
            message = _build_unknown_response_message(status, headers)

        super().__init__(
            code=ClientErrorCode.ResponseError.value,
            status=status,
            message=message,
            headers=headers,
            raw_body_text=raw_body_text,
            additional_data=None,
        )

    @staticmethod
    def is_unknown_http_response_error(error: Any) -> bool:
        return _is_notion_client_error_with_code(
            error,
            {ClientErrorCode.ResponseError.value},
        )


_api_error_codes: Set[str] = {
    APIErrorCode.Unauthorized.value,
    APIErrorCode.RestrictedResource.value,
    APIErrorCode.ObjectNotFound.value,
    APIErrorCode.RateLimited.value,
    APIErrorCode.InvalidJSON.value,
    APIErrorCode.InvalidRequestURL.value,
    APIErrorCode.InvalidRequest.value,
    APIErrorCode.ValidationError.value,
    APIErrorCode.ConflictError.value,
    APIErrorCode.InternalServerError.value,
    APIErrorCode.ServiceUnavailable.value,
    APIErrorCode.GatewayTimeout.value,
}


class APIResponseError(HTTPResponseError):
    code: APIErrorCode
    request_id: Optional[str]

    @staticmethod
    def is_api_response_error(error: Any) -> TypeGuard["APIResponseError"]:
        return _is_notion_client_error_with_code(error, _api_error_codes)


# Type alias for all Notion client errors
NotionClientError = Union[
    RequestTimeoutError,
    UnknownHTTPResponseError,
    APIResponseError,
    InvalidPathParameterError,
]


def build_request_error(
    response: httpx.Response,
    body_text: str,
) -> Union[APIResponseError, UnknownHTTPResponseError]:
    api_error_response_body = _parse_api_error_response_body(body_text)

    if api_error_response_body is not None:
        return APIResponseError(
            code=api_error_response_body["code"],
            message=api_error_response_body["message"],
            headers=response.headers,
            status=response.status_code,
            raw_body_text=body_text,
            additional_data=api_error_response_body.get("additional_data"),
            request_id=api_error_response_body.get("request_id"),
        )

    return UnknownHTTPResponseError(
        message=None,
        headers=response.headers,
        status=response.status_code,
        raw_body_text=body_text,
    )


def _build_unknown_response_message(status: int, headers: httpx.Headers) -> str:
    """Builds the default message for an unrecognized HTTP response.

    A response with a Cloudflare Ray ID but no Notion request ID was answered
    before it reached the API. The message surfaces the Ray ID rather than
    leaving callers to infer it from an HTML body.
    """
    base = f"Request to Notion API failed with status: {status}"
    ray_id = _get_response_header(headers, "cf-ray")
    request_id = _get_response_header(headers, "x-notion-request-id")
    answered_by_edge = ray_id is not None and request_id is None
    if not answered_by_edge:
        return base

    content_type = _get_response_header(headers, "content-type")
    content_type_note = (
        f" (content-type: {content_type})" if content_type is not None else ""
    )
    blocked_request_note = (
        " This may mean the request was blocked by a network security rule."
        if status == 403
        else ""
    )
    return (
        f"{base}. The response was returned by Notion's edge proxy"
        f" before reaching the Notion API{content_type_note}."
        f"{blocked_request_note}"
        f" Cloudflare Ray ID: {ray_id}."
        " Include this ID when contacting Notion support."
    )


def _parse_api_error_response_body(body: str) -> Optional[Dict[str, Any]]:
    if not isinstance(body, str):
        return None

    try:
        parsed = json.loads(body)
    except (json.JSONDecodeError, ValueError):
        return None

    if not isinstance(parsed, dict):
        return None

    message = parsed.get("message")
    code = parsed.get("code")

    if not isinstance(message, str) or not _is_api_error_code(code):
        return None

    result: Dict[str, Any] = {
        "code": APIErrorCode(code),
        "message": message,
    }

    if "additional_data" in parsed:
        result["additional_data"] = parsed["additional_data"]

    if "request_id" in parsed:
        result["request_id"] = parsed["request_id"]

    return result


def _is_api_error_code(code: Any) -> bool:
    return isinstance(code, str) and code in _api_error_codes
