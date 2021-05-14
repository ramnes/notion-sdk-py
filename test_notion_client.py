import pytest

from notion_client import AsyncClient, Client


def test_initialize_client():
    client = Client({"auth": "foo"})
    assert client

    client = AsyncClient({"auth": "foo"})
    assert client
