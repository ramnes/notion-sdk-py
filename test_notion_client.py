from notion_client import AsyncClient, Client


def test_initialize_client():
    client = Client({"auth": "foo"})
    assert client

    async_client = AsyncClient({"auth": "foo"})
    assert async_client
