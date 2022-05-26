from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from notion_client.client import Client


@pytest.mark.vcr()
def test_endpoint_blocks_retrieve(client: "Client"):
    block_id = "b8624a96-0a9e-4b14-8ef8-464aae13f9b9"

    response: Any = client.blocks.retrieve(block_id=block_id)

    assert response["id"] == block_id
    assert response["object"] == "block"


@pytest.mark.vcr()
def test_endpoint_blocks_update(client: "Client"):
    block_id = "0f06f246-1250-4da8-9100-f8fe0a537433"

    response: Any = client.blocks.update(
        block_id=block_id,
        to_do={
            "text": [{"type": "text", "text": {"content": "Lacinato kale"}}],
            "checked": False,
        },
    )

    assert response["id"] == block_id
    assert response["type"] == "to_do"
    assert not response["to_do"]["checked"]


@pytest.mark.vcr()
def test_endpoint_blocks_delete(client: "Client"):
    block_id = "3940db22-35c6-4b39-9db4-615f7485aa34"

    response: Any = client.blocks.delete(
        block_id=block_id,
    )

    assert response["id"] == block_id
    assert response["object"] == "block"
    assert response["archived"]
