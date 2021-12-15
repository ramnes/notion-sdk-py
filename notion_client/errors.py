"""Custom exceptions for notion-sdk-py.

This module defines the exceptions that can be raised when an error occurs.
"""
from enum import Enum
from typing import Optional

import httpx


class RequestTimeoutError(Exception):
    """Exception for requests that timeout.

    The request that we made waits for a specified period of time or maximum number of
    retries to get the response. But if no response comes within the limited time or
    retries, then this Exception is raised.
    """

    code = "notionhq_client_request_timeout"

    def __init__(self, message: str = "Request to Notion API has timed out") -> None:
        super().__init__(message)


class HTTPResponseError(Exception):
    """Exception for HTTP errors.

    Responses from the API use HTTP response codes that are used to indicate general
    classes of success and error.
    """

    code: str = "notionhq_client_response_error"
    status: int
    headers: httpx.Headers
    body: str

    def __init__(self, response: httpx.Response, message: Optional[str] = None) -> None:
        if message is None:
            message = (
                f"Request to Notion API failed with status: {response.status_code}"
            )
        super().__init__(message)
        self.status = response.status_code
        self.headers = response.headers
        self.body = response.text


class APIErrorCode(str, Enum):
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


class APIResponseError(HTTPResponseError):
    """An error raised by Notion API."""

    code: APIErrorCode

    def __init__(
        self, response: httpx.Response, message: str, code: APIErrorCode
    ) -> None:
        super().__init__(response, message)
        self.code = code


def is_api_error_code(code: str) -> bool:
    """Check if given code belongs to the list of valid API error codes."""
    if isinstance(code, str):
        return code in (error_code.value for error_code in APIErrorCode)
    return False


def is_timeout_error_code(code: str) -> bool:
    """Check if given code belongs to httpx timeout error codes."""
    timeouts = [
        httpx._status_codes.codes.GATEWAY_TIMEOUT,
        httpx._status_codes.codes.REQUEST_TIMEOUT,
    ]

    if isinstance(code, str):
        return code in (str(error_code.value) for error_code in timeouts)
    return False
