import logging
from dataclasses import dataclass
from typing import Dict, Union

import httpx

from .api_endpoints import (
    BlocksEndpoint,
    DatabasesEndpoint,
    PagesEndpoint,
    UsersEndpoint,
)
from .errors import build_request_error
from .helpers import pick
from .logging import make_console_logger


@dataclass
class ClientOptions:
    auth: str = None
    timeout_ms: int = 60_000
    base_url: str = "https://api.notion.com"
    log_level: int = logging.WARNING
    logger: logging.Logger = None
    notion_version: str = "2021-05-13"


class Client:
    def __init__(
        self,
        options: Union[Dict, ClientOptions] = None,
        client: httpx.Client = None,
        **kwargs,
    ):
        if options is None:
            options = ClientOptions(**kwargs)
        elif isinstance(options, dict):
            options = ClientOptions(**options)

        self.logger = options.logger or make_console_logger()
        self.logger.setLevel(options.log_level)

        if client is None:
            client = httpx.Client()
        self.client = client
        self.client.base_url = options.base_url + "/v1/"
        self.client.timeout = options.timeout_ms / 1_000
        self.client.headers = {
            "Notion-Version": options.notion_version,
            "User-Agent": "ramnes/notion-sdk-py@0.3.1",
        }
        if options.auth:
            self.client.headers["Authorization"] = f"Bearer {options.auth}"

        self.blocks = BlocksEndpoint(self)
        self.databases = DatabasesEndpoint(self)
        self.users = UsersEndpoint(self)
        self.pages = PagesEndpoint(self)

    def _build_request(self, method, path, query, body):
        self.logger.info(f"{method} {self.client.base_url}{path}")
        return self.client.build_request(method, path, params=query, json=body)

    def _check_response(self, response):
        try:
            response.raise_for_status()
        except Exception as error:
            raise build_request_error(error) or error

    def request(self, path, method, query=None, body=None, auth=None):
        request = self._build_request(method, path, query, body)
        response = self.client.send(request)
        self._check_response(response)
        return response

    def search(self, **kwargs):
        return self.request(
            path="search",
            method="POST",
            body=pick(kwargs, "query", "sort", "filter", "start_cursor", "page_size"),
        )


class AsyncClient(Client):
    def __init__(
        self,
        options: Union[Dict, ClientOptions] = None,
        client: httpx.AsyncClient = None,
        **kwargs,
    ):
        if client is None:
            client = httpx.AsyncClient()
        super().__init__(options, client, **kwargs)

    async def request(self, path, method, query=None, body=None, auth=None):
        request = self._build_request(method, path, query, body)
        async with self.client as client:
            response = await client.send(request)
        response.raise_for_status()
        self._check_response(response)
        return response
