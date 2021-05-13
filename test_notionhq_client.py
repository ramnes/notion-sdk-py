import pytest

from notionhq_client import Client


def test_initialize_client():
    client = Client({"auth": "foo"})
    assert client
