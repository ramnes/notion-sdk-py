"""Custom type definitions for notion-sdk-py."""
from typing import Awaitable, TypeVar, Union, TypedDict

T = TypeVar("T")
SyncAsync = Union[T, Awaitable[T]]


class OAuthHeader(TypedDict):
    client_id: str
    client_secret: str
