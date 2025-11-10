"""Custom exceptions for notion-sdk-py.

This module defines the exceptions that can be raised when an error occurs.
"""

import asyncio
import json
from enum import Enum
from typing import Any, Dict, Optional, Union

import httpx



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


class ClientErrorCode(str, Enum):
    """Error codes generated for client errors."""

    RequestTimeout = "notionhq_client_request_timeout"
    ResponseError = "notionhq_client_response_error"


# Error codes on errors thrown by the `Client`.
NotionErrorCode = Union[APIErrorCode, ClientErrorCode]


class NotionClientErrorBase(Exception):
    """Base error type for all Notion client errors."""

    def __init__(self, message: str = "") -> None:
        super().__init__(message)


def is_notion_client_error(error: Any) -> bool:
    return isinstance(error, NotionClientErrorBase)


def is_notion_client_error_with_code(error: Any, codes: Dict[str, bool]) -> bool:
    if not is_notion_client_error(error):
        return False

    # Get the code value as string for comparison
    error_code = error.code
    if isinstance(error_code, Enum):
        error_code = error_code.value

    return error_code in codes


class RequestTimeoutError(NotionClientErrorBase):
    """Error thrown by the client if a request times out."""

    code: str = ClientErrorCode.RequestTimeout

    def __init__(self, message: str = "Request to Notion API has timed out") -> None:
        super().__init__(message)

    @staticmethod
    def is_request_timeout_error(error: Any) -> bool:
        """Check if the error is a RequestTimeoutError.

        Args:
            error: Any value, usually a caught exception.

        Returns:
            True if error is a RequestTimeoutError.
        """
        return is_notion_client_error_with_code(error, {
            ClientErrorCode.RequestTimeout.value: True,
        })

    @staticmethod
    async def reject_after_timeout(coro: Any, timeout_ms: int) -> Any:
        try:
            return await asyncio.wait_for(coro, timeout=timeout_ms / 1000.0)
        except asyncio.TimeoutError:
            raise RequestTimeoutError()


HTTPResponseErrorCode = Union[ClientErrorCode, APIErrorCode]


class HTTPResponseError(NotionClientErrorBase):

    code: str
    status: int
    headers: httpx.Headers
    body: str
    additional_data: Optional[Dict[str, Any]]
    request_id: Optional[str]

    def __init__(
        self,
        code: str,
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
        self.request_id = request_id


_http_response_error_codes: Dict[str, bool] = {
    ClientErrorCode.ResponseError.value: True,
    APIErrorCode.Unauthorized.value: True,
    APIErrorCode.RestrictedResource.value: True,
    APIErrorCode.ObjectNotFound.value: True,
    APIErrorCode.RateLimited.value: True,
    APIErrorCode.InvalidJSON.value: True,
    APIErrorCode.InvalidRequestURL.value: True,
    APIErrorCode.InvalidRequest.value: True,
    APIErrorCode.ValidationError.value: True,
    APIErrorCode.ConflictError.value: True,
    APIErrorCode.InternalServerError.value: True,
    APIErrorCode.ServiceUnavailable.value: True,
}


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
        if message is None:
            message = f"Request to Notion API failed with status: {status}"
        if headers is None:
            headers = httpx.Headers()

        super().__init__(
            code=ClientErrorCode.ResponseError.value,
            status=status,
            message=message,
            headers=headers,
            raw_body_text=raw_body_text,
            additional_data=None,
            request_id=None,
        )

    @staticmethod
    def is_unknown_http_response_error(error: Any) -> bool:
        """Check if the error is an UnknownHTTPResponseError.

        Args:
            error: Any value, usually a caught exception.

        Returns:
            True if error is an UnknownHTTPResponseError.
        """
        return is_notion_client_error_with_code(error, {
            ClientErrorCode.ResponseError.value: True,
        })


_api_error_codes: Dict[str, bool] = {
    APIErrorCode.Unauthorized.value: True,
    APIErrorCode.RestrictedResource.value: True,
    APIErrorCode.ObjectNotFound.value: True,
    APIErrorCode.RateLimited.value: True,
    APIErrorCode.InvalidJSON.value: True,
    APIErrorCode.InvalidRequestURL.value: True,
    APIErrorCode.InvalidRequest.value: True,
    APIErrorCode.ValidationError.value: True,
    APIErrorCode.ConflictError.value: True,
    APIErrorCode.InternalServerError.value: True,
    APIErrorCode.ServiceUnavailable.value: True,
}


class APIResponseError(HTTPResponseError):
    # Override the code type annotation for better type checking
    code: APIErrorCode

    def __init__(
        self,
        code: APIErrorCode,
        status: int,
        message: str,
        headers: httpx.Headers,
        raw_body_text: str,
        additional_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        # Store the enum directly, not just the value
        # This is different from the parent class to maintain type information
        super().__init__(
            code=code.value if isinstance(code, APIErrorCode) else code,
            status=status,
            message=message,
            headers=headers,
            raw_body_text=raw_body_text,
            additional_data=additional_data,
            request_id=request_id,
        )
        # Override with the actual enum for type-safe access
        self.code = code if isinstance(code, APIErrorCode) else APIErrorCode(code)

    @staticmethod
    def is_api_response_error(error: Any) -> bool:
        return is_notion_client_error_with_code(error, _api_error_codes)


# Type alias for all Notion client errors
NotionClientError = Union[RequestTimeoutError, UnknownHTTPResponseError, APIResponseError]


def is_http_response_error(error: Any) -> bool:
    return is_notion_client_error_with_code(error, _http_response_error_codes)


def build_request_error(
    response: httpx.Response,
    body_text: str,
) -> Union[APIResponseError, UnknownHTTPResponseError]:
    """Build an appropriate error object from an HTTP response.

    Args:
        response: The HTTP response object.
        body_text: The raw response body text.

    Returns:
        Either an APIResponseError if the response contains a valid API error,
        or an UnknownHTTPResponseError otherwise.
    """
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

    if not isinstance(message, str) or not is_api_error_code(code):
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


def is_api_error_code(code: Any) -> bool:
    if isinstance(code, str):
        return code in _api_error_codes
    return False
