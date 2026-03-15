"""Synchronous and asynchronous clients for Notion's API."""

import asyncio
import base64
import logging
import math
import random
import time
from abc import abstractmethod
from dataclasses import dataclass, field
from email.utils import parsedate_to_datetime
from types import TracebackType
from typing import Any, Dict, List, Optional, Type, Union

import httpx
from httpx import Request, Response

from notion_client.api_endpoints import (
    BlocksEndpoint,
    CommentsEndpoint,
    DatabasesEndpoint,
    DataSourcesEndpoint,
    PagesEndpoint,
    SearchEndpoint,
    UsersEndpoint,
    FileUploadsEndpoint,
    OAuthEndpoint,
)
from notion_client.errors import (
    APIErrorCode,
    APIResponseError,
    build_request_error,
    is_http_response_error,
    is_notion_client_error,
    NotionClientError,
    RequestTimeoutError,
    validate_request_path,
)
from notion_client.logging import make_console_logger
from notion_client.typing import SyncAsync


@dataclass
class RetryOptions:
    """Configuration for automatic retries on rate limit (429) and server errors.

    Attributes:
        max_retries: Maximum number of retry attempts. Set to 0 to disable retries.
        initial_retry_delay_ms: Initial delay between retries in milliseconds.
            Used as base for exponential back-off when retry-after header is absent.
        max_retry_delay_ms: Maximum delay between retries in milliseconds.
    """

    max_retries: int = 2
    initial_retry_delay_ms: int = 1000
    max_retry_delay_ms: int = 60_000


@dataclass
class ClientOptions:
    """Options to configure the client.

    Attributes:
        auth: Bearer token for authentication. If left undefined, the `auth` parameter
            should be set on each request.
        timeout_ms: Number of milliseconds to wait before emitting a
            `RequestTimeoutError`.
        base_url: The root URL for sending API requests. This can be changed to test
            with a mock server.
        log_level: Verbosity of logs the instance will produce. By default, logs are
            written to `stdout`.
        logger: A custom logger.
        notion_version: Notion version to use.
        retry: Configuration for automatic retries on rate limit (429) and server errors.
            Set to False to disable retries entirely.
    """

    auth: Optional[str] = None
    timeout_ms: int = 60_000
    base_url: str = "https://api.notion.com"
    log_level: int = logging.WARNING
    logger: Optional[logging.Logger] = None
    notion_version: str = "2025-09-03"
    retry: Union[RetryOptions, bool] = field(default_factory=RetryOptions)


class BaseClient:
    def __init__(
        self,
        client: Union[httpx.Client, httpx.AsyncClient],
        options: Optional[Union[Dict[str, Any], ClientOptions]] = None,
        **kwargs: Any,
    ) -> None:
        if options is None:
            options = ClientOptions(**kwargs)
        elif isinstance(options, dict):
            options = ClientOptions(**options)

        self.logger = options.logger or make_console_logger()
        self.logger.setLevel(options.log_level)
        self.options = options

        if options.retry is False:
            self._max_retries = 0
            self._initial_retry_delay_ms = 0
            self._max_retry_delay_ms = 0
        elif isinstance(options.retry, RetryOptions):
            self._max_retries = options.retry.max_retries
            self._initial_retry_delay_ms = options.retry.initial_retry_delay_ms
            self._max_retry_delay_ms = options.retry.max_retry_delay_ms
        else:
            retry_opts = RetryOptions()
            self._max_retries = retry_opts.max_retries
            self._initial_retry_delay_ms = retry_opts.initial_retry_delay_ms
            self._max_retry_delay_ms = retry_opts.max_retry_delay_ms

        self._clients: List[Union[httpx.Client, httpx.AsyncClient]] = []
        self.client = client

        self.blocks = BlocksEndpoint(self)
        self.databases = DatabasesEndpoint(self)
        self.data_sources = DataSourcesEndpoint(self)
        self.users = UsersEndpoint(self)
        self.pages = PagesEndpoint(self)
        self.search = SearchEndpoint(self)
        self.comments = CommentsEndpoint(self)
        self.file_uploads = FileUploadsEndpoint(self)
        self.oauth = OAuthEndpoint(self)

    @property
    def client(self) -> Union[httpx.Client, httpx.AsyncClient]:
        return self._clients[-1]

    @client.setter
    def client(self, client: Union[httpx.Client, httpx.AsyncClient]) -> None:
        client.base_url = httpx.URL(f"{self.options.base_url}/v1/")
        client.timeout = httpx.Timeout(timeout=self.options.timeout_ms / 1_000)
        client.headers = httpx.Headers(
            {
                "Notion-Version": self.options.notion_version,
                "User-Agent": "ramnes/notion-sdk-py@3.0.0",
            }
        )
        if self.options.auth:
            client.headers["Authorization"] = f"Bearer {self.options.auth}"
        self._clients.append(client)

    def _build_request(
        self,
        method: str,
        path: str,
        query: Optional[Dict[Any, Any]] = None,
        body: Optional[Dict[Any, Any]] = None,
        form_data: Optional[Dict[Any, Any]] = None,
        auth: Optional[Union[str, Dict[str, str]]] = None,
    ) -> Request:
        headers = httpx.Headers()
        if auth:
            if isinstance(auth, dict):
                client_id = auth.get("client_id", "")
                client_secret = auth.get("client_secret", "")
                credentials = f"{client_id}:{client_secret}"
                encoded_credentials = base64.b64encode(credentials.encode()).decode()
                headers["Authorization"] = f"Basic {encoded_credentials}"
            else:
                headers["Authorization"] = f"Bearer {auth}"

        if not form_data:
            return self.client.build_request(
                method,
                path,
                params=query,
                json=body,
                headers=headers,
            )

        files: Dict[str, Any] = {}
        data: Dict[str, Any] = {}
        for key, value in form_data.items():
            if isinstance(value, tuple) and len(value) >= 2:
                files[key] = value
            elif hasattr(value, "read"):
                files[key] = value
            elif isinstance(value, str):
                data[key] = value
            else:
                data[key] = str(value)

        return self.client.build_request(
            method,
            path,
            params=query,
            files=files,
            data=data,
            headers=headers,
        )

    def _parse_response(self, response: Response) -> Any:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            body_text = error.response.text
            raise build_request_error(error.response, body_text)

        return response.json()

    def _extract_request_id(self, obj: Any) -> Optional[str]:
        """Extracts request_id from an object if present."""
        if isinstance(obj, dict):
            return obj.get("request_id")
        else:
            request_id = getattr(obj, "request_id", None)
        return request_id if isinstance(request_id, str) else None

    def _log_request_success(self, method: str, path: str, response_body: Any) -> None:
        """Logs a successful request."""
        request_id = self._extract_request_id(response_body)
        msg = f"request success: method={method}, path={path}"
        if request_id:
            msg += f", request_id={request_id}"
        self.logger.info(msg)

    def _log_request_error(self, error: NotionClientError, attempt: int = 0) -> None:
        """Logs a request error with appropriate detail level."""
        request_id = self._extract_request_id(error)
        msg = f"request fail: code={error.code}, message={error}, attempt={attempt}"
        if request_id:
            msg += f", request_id={request_id}"
        self.logger.warning(msg)
        if is_http_response_error(error):
            self.logger.debug(f"failed response body: {error.body}")

    def _can_retry(self, error: Exception, method: str) -> bool:
        """Determines if an error can be retried based on its error code and method.

        Rate limits (429) are always retryable since the server explicitly asks us to retry.
        Server errors (500, 503) are only retried for idempotent methods
        (GET, DELETE) to avoid duplicate side effects.
        """
        if not APIResponseError.is_api_response_error(error):
            return False

        # Rate limits are always retryable - server says "try again later"
        if error.code == APIErrorCode.RateLimited:
            return True

        # Server errors only retry for idempotent methods
        is_idempotent = method.upper() in ("GET", "DELETE")
        if is_idempotent:
            return error.code in (
                APIErrorCode.InternalServerError,
                APIErrorCode.ServiceUnavailable,
            )

        return False

    def _calculate_retry_delay(self, error: Exception, attempt: int) -> float:
        """Calculates the delay before the next retry attempt.

        Uses retry-after header if present, otherwise exponential back-off with jitter.
        Returns delay in seconds.
        """
        if APIResponseError.is_api_response_error(error):
            retry_after_ms = self._parse_retry_after_header(error.headers)
            if retry_after_ms is not None:
                return min(retry_after_ms, self._max_retry_delay_ms) / 1000.0

        # Exponential back-off with full jitter
        base_delay = self._initial_retry_delay_ms * math.pow(2, attempt)
        jitter = random.random()
        delay = (
            min(base_delay * jitter + base_delay / 2, self._max_retry_delay_ms) / 1000.0
        )
        return delay

    def _parse_retry_after_header(self, headers: httpx.Headers) -> Optional[float]:
        """Parses the retry-after header value.

        Supports both delta-seconds (e.g., "120") and HTTP-date formats.
        Returns the delay in milliseconds, or None if not present or invalid.
        """
        retry_after_value = headers.get("retry-after")
        if not retry_after_value:
            return None

        # Try parsing as delta-seconds (integer)
        try:
            seconds = int(retry_after_value)
            if seconds >= 0:
                return seconds * 1000.0
        except ValueError:
            pass

        # Try parsing as HTTP-date
        try:
            retry_date = parsedate_to_datetime(retry_after_value)
            delay_ms = (retry_date.timestamp() - time.time()) * 1000.0
            return delay_ms if delay_ms > 0 else 0.0
        except (ValueError, TypeError):
            pass

        return None

    @abstractmethod
    def request(
        self,
        path: str,
        method: str,
        query: Optional[Dict[Any, Any]] = None,
        body: Optional[Dict[Any, Any]] = None,
        form_data: Optional[Dict[Any, Any]] = None,
        auth: Optional[Union[str, Dict[str, str]]] = None,
    ) -> SyncAsync[Any]:
        # noqa
        pass


class Client(BaseClient):
    """Synchronous client for Notion's API."""

    client: httpx.Client

    def __init__(
        self,
        options: Optional[Union[Dict[Any, Any], ClientOptions]] = None,
        client: Optional[httpx.Client] = None,
        **kwargs: Any,
    ) -> None:
        if client is None:
            client = httpx.Client()
        super().__init__(client, options, **kwargs)

    def __enter__(self) -> "Client":
        self.client = httpx.Client()
        self.client.__enter__()
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        self.client.__exit__(exc_type, exc_value, traceback)
        del self._clients[-1]

    def close(self) -> None:
        """Close the connection pool of the current inner client."""
        self.client.close()

    def request(
        self,
        path: str,
        method: str,
        query: Optional[Dict[Any, Any]] = None,
        body: Optional[Dict[Any, Any]] = None,
        form_data: Optional[Dict[Any, Any]] = None,
        auth: Optional[Union[str, Dict[str, str]]] = None,
    ) -> Any:
        """Send an HTTP request."""
        validate_request_path(path)
        self.logger.info(f"{method} {self.client.base_url}{path}")
        return self._execute_with_retry(method, path, query, body, form_data, auth)

    def _execute_with_retry(
        self,
        method: str,
        path: str,
        query: Optional[Dict[Any, Any]],
        body: Optional[Dict[Any, Any]],
        form_data: Optional[Dict[Any, Any]],
        auth: Optional[Union[str, Dict[str, str]]],
    ) -> Any:
        """Executes the request with retry logic."""
        attempt = 0
        while True:
            request = self._build_request(method, path, query, body, form_data, auth)
            try:
                return self._execute_single_request(request, method, path)
            except Exception as error:
                if not is_notion_client_error(error):
                    raise error

                self._log_request_error(error, attempt)

                if attempt >= self._max_retries or not self._can_retry(error, method):
                    raise error

                delay = self._calculate_retry_delay(error, attempt)
                self.logger.info(
                    f"retrying request: method={method}, path={path}, attempt={attempt + 1}, delay_ms={delay * 1000:.0f}"
                )
                time.sleep(delay)
                attempt += 1

    def _execute_single_request(self, request: Request, method: str, path: str) -> Any:
        """Executes a single HTTP request (no retry)."""
        try:
            response = self.client.send(request)
        except httpx.TimeoutException:
            raise RequestTimeoutError()
        response_body = self._parse_response(response)
        self._log_request_success(method, path, response_body)
        return response_body


class AsyncClient(BaseClient):
    """Asynchronous client for Notion's API."""

    client: httpx.AsyncClient

    def __init__(
        self,
        options: Optional[Union[Dict[str, Any], ClientOptions]] = None,
        client: Optional[httpx.AsyncClient] = None,
        **kwargs: Any,
    ) -> None:
        if client is None:
            client = httpx.AsyncClient()
        super().__init__(client, options, **kwargs)

    async def __aenter__(self) -> "AsyncClient":
        self.client = httpx.AsyncClient()
        await self.client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        await self.client.__aexit__(exc_type, exc_value, traceback)
        del self._clients[-1]

    async def aclose(self) -> None:
        """Close the connection pool of the current inner client."""
        await self.client.aclose()

    async def request(
        self,
        path: str,
        method: str,
        query: Optional[Dict[Any, Any]] = None,
        body: Optional[Dict[Any, Any]] = None,
        form_data: Optional[Dict[Any, Any]] = None,
        auth: Optional[Union[str, Dict[str, str]]] = None,
    ) -> Any:
        """Send an HTTP request asynchronously."""
        validate_request_path(path)
        self.logger.info(f"{method} {self.client.base_url}{path}")
        return await self._execute_with_retry(
            method, path, query, body, form_data, auth
        )

    async def _execute_with_retry(
        self,
        method: str,
        path: str,
        query: Optional[Dict[Any, Any]],
        body: Optional[Dict[Any, Any]],
        form_data: Optional[Dict[Any, Any]],
        auth: Optional[Union[str, Dict[str, str]]],
    ) -> Any:
        """Executes the request with retry logic."""
        attempt = 0
        while True:
            request = self._build_request(method, path, query, body, form_data, auth)
            try:
                return await self._execute_single_request(request, method, path)
            except Exception as error:
                if not is_notion_client_error(error):
                    raise error

                self._log_request_error(error, attempt)

                if attempt >= self._max_retries or not self._can_retry(error, method):
                    raise error

                delay = self._calculate_retry_delay(error, attempt)
                self.logger.info(
                    f"retrying request: method={method}, path={path}, attempt={attempt + 1}, delay_ms={delay * 1000:.0f}"
                )
                await asyncio.sleep(delay)
                attempt += 1

    async def _execute_single_request(
        self, request: Request, method: str, path: str
    ) -> Any:
        """Executes a single HTTP request (no retry)."""
        try:
            response = await self.client.send(request)
        except httpx.TimeoutException:
            raise RequestTimeoutError()
        response_body = self._parse_response(response)
        self._log_request_success(method, path, response_body)
        return response_body
