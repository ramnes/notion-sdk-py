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
    client = Client(auth="Invalid")

    with pytest.raises(APIResponseError):
        client.request("/users", "GET")

    response = client.request("/users", "GET", auth=token)
    assert response["results"]

    client.close()


@pytest.mark.vcr()
async def test_async_client_request_auth(token):
    async_client = AsyncClient(auth="Invalid")

    with pytest.raises(APIResponseError):
        await async_client.request("/users", "GET")

    response = await async_client.request("/users", "GET", auth=token)
    assert response["results"]

    await async_client.aclose()


@pytest.mark.vcr()
def test_client_request_oauth(token, client_id, client_secret):
    client = Client()

    with pytest.raises(APIResponseError):
        client.request("/oauth/introspect", "POST")

    with pytest.raises(APIResponseError):
        client.request("/oauth/introspect", "POST", auth="STRING_INVALID")

    response = client.request(
        "/oauth/introspect",
        "POST",
        auth={"client_id": client_id, "client_secret": client_secret},
        body={"token": token},
    )
    assert response

    client.close()
