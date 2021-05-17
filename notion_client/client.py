import logging
from abc import abstractclassmethod
from dataclasses import dataclass
from typing import Any, Awaitable, Dict, Optional, Union

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
    APIErrorResponseBody,
    APIResponseError,
    HTTPResponseError,
    RequestTimeoutError,
    is_api_error_code,
    is_timeout_error,
)
from notion_client.logging import make_console_logger


@dataclass
class ClientOptions:
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
                "User-Agent": "ramnes/notion-sdk-py@0.3.1",
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
    ) -> Request:
        self.logger.info(f"{method} {self.client.base_url}{path}")
        return self.client.build_request(method, path, params=query, json=body)

    def _check_response(self, response: Response) -> None:
        try:
            response.raise_for_status()
        except httpx.TimeoutException as error:
            if is_timeout_error(error):
                raise RequestTimeoutError()
            raise
        except httpx.HTTPStatusError as error:
            body = error.response.json()
            code = body.get("code")
            if is_api_error_code(code):
                body = APIErrorResponseBody(code=code, message=body["message"])
                raise APIResponseError(error.response, body)
            raise HTTPResponseError(error.response)

    @abstractclassmethod
    def request(
        self,
        path: str,
        method: str,
        query: Optional[Dict[Any, Any]] = None,
        body: Optional[Dict[Any, Any]] = None,
        auth: Optional[str] = None,
    ) -> Union[Response, Awaitable[Response]]:
        pass


class Client(BaseClient):
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
    ) -> Response:
        request = self._build_request(method, path, query, body)
        response = self.client.send(request)
        self._check_response(response)
        return response


class AsyncClient(BaseClient):
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
    ) -> Response:
        request = self._build_request(method, path, query, body)
        if not isinstance(self.client, httpx.AsyncClient):
            raise Exception("httpx.AsyncClient was expected")
        async with self.client as client:
            response = await client.send(request)
        self._check_response(response)
        return response
