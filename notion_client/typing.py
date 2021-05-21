"""Custom type definitions for notion-sdk-py."""

from typing import Awaitable, TypeVar, Union

T = TypeVar("T")
SyncAsync = Union[T, Awaitable[T]]
