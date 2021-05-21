"""Custom Exceptions for notion-sdk-py.

This module defines python Exceptions that are raised when their
corresponding HTTP response codes are returned by Notion API.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import httpx


class RequestTimeoutError(Exception):
    """Request timed out.

    The request that we made waits for a specified period of time or maximum number
    of retries to get the response.
    But if no response comes within the limited time or retries,
    then this Exception is raised.
    """

    code = "notionhq_client_request_timeout"

    def __init__(self, message: str = "Request to Notion API has timed out") -> None:
        """Initialize  RequestTimeoutError."""
        super().__init__(message)
        self.name = "RequestTimeoutError"

    @staticmethod
    def is_request_timeout_error(e: Exception) -> bool:
        """Check if Exception is an request timeout error."""
        return (
            isinstance(e, RequestTimeoutError)
            and hasattr(e, "code")
            and e.code == RequestTimeoutError.code
        )


class HTTPResponseError(Exception):
    """HTTP Response Errors.

    Responses from the API use HTTP response codes that are used to
    indicate general classes of success and error.
    """

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
        """Check if Exception is an http response error."""
        return (
            isinstance(e, HTTPResponseError)
            and hasattr(e, "code")
            and e.code == HTTPResponseError.code
        )


class APIErrorCode(str, Enum):
    """Enumerate API error codes."""

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


@dataclass
class APIErrorResponseBody:
    code: APIErrorCode
    message: str


class APIResponseError(HTTPResponseError):
    """An error raised by Notion API."""

    code: APIErrorCode

    def __init__(self, response: httpx.Response, body: APIErrorResponseBody) -> None:
        """Initialize api response error."""
        super().__init__(response, body.message)
        self.code = body.code

    @staticmethod
    def is_api_response_error(e: Exception) -> bool:
        """Check if Exception is an API response error."""
        return (
            isinstance(e, APIResponseError)
            and hasattr(e, "code")
            and is_api_error_code(e.code)
        )


# Type Guards


def is_api_error_code(code: str) -> bool:
    """Check if given code belongs to the list of valid API error codes."""
    codes = [error_code.value for error_code in APIErrorCode]
    return type(code) == str and code in codes


def is_timeout_error(e: Exception) -> bool:
    """Check if Exception is a timeout error."""
    return (
        isinstance(e, httpx.TimeoutException)
        and hasattr(e, "request")
        and isinstance(e.request, httpx.Request)
    )


def is_http_error(e: Exception) -> bool:
    """Check if Exception is an HTTP error."""
    return (
        isinstance(e, httpx.HTTPStatusError)
        and hasattr(e, "request")
        and hasattr(e, "response")
        and isinstance(e.request, httpx.Request)
        and isinstance(e.response, httpx.Response)
    )
