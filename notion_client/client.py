"""Synchronous and asynchronous clients for Notion's API."""
import logging
from abc import abstractclassmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

import httpx
from httpx import Request, Response

from notion_client.api_endpoints import (
    BlocksEndpoint,
    DatabasesEndpoint,
    PagesEndpoint,
    SearchEndpoint,
    UsersEndpoint,
)
from notion_client.errors import (
    APIResponseError,
    HTTPResponseError,
    RequestTimeoutError,
    is_api_error_code,
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
        base_url: The root URL for sending API requests. This can be changed to test with
            a mock server.
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
    notion_version: str = "2021-05-13"


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

        self.client = client
        self.client.base_url = httpx.URL(options.base_url + "/v1/")
        self.client.timeout = httpx.Timeout(timeout=options.timeout_ms / 1_000)
        self.client.headers = httpx.Headers(
            {
                "Notion-Version": options.notion_version,
                "User-Agent": "ramnes/notion-sdk-py@0.5.0",
            }
        )
        if options.auth:
            self.client.headers["Authorization"] = f"Bearer {options.auth}"

        self.blocks = BlocksEndpoint(self)
        self.databases = DatabasesEndpoint(self)
        self.users = UsersEndpoint(self)
        self.pages = PagesEndpoint(self)
        self.search = SearchEndpoint(self)

    def _build_request(
        self,
        method: str,
        path: str,
        query: Optional[Dict[Any, Any]] = None,
        body: Optional[Dict[Any, Any]] = None,
        auth: Optional[str] = None,
    ) -> Request:
        headers = httpx.Headers()
        if auth:
            headers["Authorization"] = f"Bearer {auth}"
        self.logger.info(f"{method} {self.client.base_url}{path}")
        return self.client.build_request(
            method, path, params=query, json=body, headers=headers
        )

    def _parse_response(self, response: Response) -> Any:
        try:
            response.raise_for_status()
        except httpx.TimeoutException:
            raise RequestTimeoutError()
        except httpx.HTTPStatusError as error:
            body = error.response.json()
            code = body.get("code")
            if code and is_api_error_code(code):
                raise APIResponseError(response, body["message"], code)
            raise HTTPResponseError(error.response)

        return response.json()

    @abstractclassmethod
    def request(
        self,
        path: str,
        method: str,
        query: Optional[Dict[Any, Any]] = None,
        body: Optional[Dict[Any, Any]] = None,
        auth: Optional[str] = None,
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

    def request(
        self,
        path: str,
        method: str,
        query: Optional[Dict[Any, Any]] = None,
        body: Optional[Dict[Any, Any]] = None,
        auth: Optional[str] = None,
    ) -> Any:
        """Send an HTTP request."""
        request = self._build_request(method, path, query, body, auth)
        response = self.client.send(request)
        return self._parse_response(response)


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

    async def request(
        self,
        path: str,
        method: str,
        query: Optional[Dict[Any, Any]] = None,
        body: Optional[Dict[Any, Any]] = None,
        auth: Optional[str] = None,
    ) -> Any:
        """Send an HTTP request asynchronously."""
        request = self._build_request(method, path, query, body, auth)
        async with self.client as client:
            response = await client.send(request)
        return self._parse_response(response)
