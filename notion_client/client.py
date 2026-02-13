"""Synchronous and asynchronous clients for Notion's API."""

import base64
import logging
from abc import abstractmethod
from dataclasses import dataclass
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
    build_request_error,
    is_http_response_error,
    is_notion_client_error,
    RequestTimeoutError,
    validate_request_path,
)
from notion_client.logging import make_console_logger
from notion_client.typing import SyncAsync


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
    """

    auth: Optional[str] = None
    timeout_ms: int = 60_000
    base_url: str = "https://api.notion.com"
    log_level: int = logging.WARNING
    logger: Optional[logging.Logger] = None
    notion_version: str = "2025-09-03"


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
                "User-Agent": "ramnes/notion-sdk-py@2.7.0",
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
        validate_request_path(path)
        if auth:
            if isinstance(auth, dict):
                client_id = auth.get("client_id", "")
                client_secret = auth.get("client_secret", "")
                credentials = f"{client_id}:{client_secret}"
                encoded_credentials = base64.b64encode(credentials.encode()).decode()
                headers["Authorization"] = f"Basic {encoded_credentials}"
            else:
                headers["Authorization"] = f"Bearer {auth}"
        self.logger.info(f"{method} {self.client.base_url}{path}")
        self.logger.debug(f"=> {query} -- {body} -- {form_data}")

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

    def _log_request_success(self, method: str, path: str, response_body: Any) -> None:
        """Logs a successful request."""
        request_id = response_body.get("request_id")
        if request_id:
            self.logger.info(
                f"request success: method={method}, path={path}, "
                f"request_id={request_id}"
            )
        else:
            self.logger.info(f"request success: method={method}, path={path}")

    def _log_request_error(self, error: Exception) -> None:
        """Logs a request error with appropriate detail level."""
        if not is_notion_client_error(error):
            raise error

        # Log the error if it's one of our known error types
        self.logger.warning(f"request fail: code={error.code}, message={error}")

        if is_http_response_error(error):
            # The response body may contain sensitive information
            # so it is logged separately at the DEBUG level
            self.logger.debug(f"failed response body: {error.body}")

        raise error

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
        request = self._build_request(method, path, query, body, form_data, auth)
        try:
            try:
                response = self.client.send(request)
            except httpx.TimeoutException:
                raise RequestTimeoutError()
            response_body = self._parse_response(response)
            self._log_request_success(method, path, response_body)
            return response_body
        except Exception as error:
            self._log_request_error(error)


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
        request = self._build_request(method, path, query, body, form_data, auth)
        try:
            try:
                response = await self.client.send(request)
            except httpx.TimeoutException:
                raise RequestTimeoutError()
            response_body = self._parse_response(response)
            self._log_request_success(method, path, response_body)
            return response_body
        except Exception as error:
            self._log_request_error(error)
