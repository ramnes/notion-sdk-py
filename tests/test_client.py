from notion_client import AsyncClient, Client


def test_initialize_client(token):
    client = Client({"auth": token})
    assert client

    async_client = AsyncClient({"auth": token})
    assert async_client
