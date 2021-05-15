import pytest

from conftest import PROPER_AUTH
from notion_client import AsyncClient, Client
from notion_client.errors import APIErrorCode


def test_initialize_client():
    client = Client({"auth": "foo"})
    assert client

    client = AsyncClient({"auth": "foo"})
    assert client


def test_list_databases():
    wrong_client = Client({"auth": "foo"})
    try:
        data = wrong_client.databases.list()
    except Exception as error:
        assert error.code == APIErrorCode.Unauthorized.value
    proper_client = Client({"auth": PROPER_AUTH})
    data = proper_client.databases.list()
    assert data == {"foo": "bar"}
