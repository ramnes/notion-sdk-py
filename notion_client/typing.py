"""Custom type definitions for notion-sdk-py."""
from typing import TYPE_CHECKING, Any, Awaitable, Mapping, TypeVar, Union

if TYPE_CHECKING:  # pragma: no cover
    from notion_client.client import BaseClient

T = TypeVar("T")
SyncAsync = Union[T, Awaitable[T]]

ClientType = TypeVar("ClientType", bound=BaseClient)
ResponseType = TypeVar("ResponseType", bound=Mapping[Any, Any])