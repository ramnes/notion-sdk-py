import pytest

from notion_client import APIResponseError, AsyncClient, Client


def test_client_init(client):
    assert isinstance(client, Client)


def test_async_client_init(async_client):
    assert isinstance(async_client, AsyncClient)


@pytest.mark.vcr()
def test_client_request(client):
    with pytest.raises(APIResponseError):
        client.request("/invalid", "GET")

    response = client.request("/users", "GET")
    assert response["results"]


@pytest.mark.vcr()
async def test_async_client_request(async_client):
    with pytest.raises(APIResponseError):
        await async_client.request("/invalid", "GET")

    response = await async_client.request("/users", "GET")
    assert response["results"]


@pytest.mark.vcr()
def test_client_request_auth(token):
    client = Client()

    with pytest.raises(APIResponseError):
        client.request("/users", "GET")

    response = client.request("/users", "GET", auth=token)
    assert response["results"]


@pytest.mark.vcr()
async def test_async_client_request_auth(token):
    client = AsyncClient()

    with pytest.raises(APIResponseError):
        await client.request("/users", "GET")

    response = await client.request("/users", "GET", auth=token)
    assert response["results"]
