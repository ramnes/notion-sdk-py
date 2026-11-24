"""Custom type definitions for notion-sdk-py."""

from typing import Any, Awaitable, Dict, TypeVar, Union

T = TypeVar("T")
SyncAsync = Union[T, Awaitable[T]]

NotionResponse = Dict[str, Any]
"""A decoded JSON response from the Notion API."""

ResponseT = TypeVar("ResponseT")
"""Return type of endpoint methods: `NotionResponse` for `Client`,
`Awaitable[NotionResponse]` for `AsyncClient`."""
