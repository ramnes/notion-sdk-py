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
