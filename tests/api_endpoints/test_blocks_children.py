from typing import TYPE_CHECKING, Any, Optional

import pytest

if TYPE_CHECKING:
    from notion_client.client import Client


@pytest.mark.vcr()
def test_endpoint_blocks_children_append(client: "Client"):
    block_id = "77897eca-aae1-4e6a-906f-e01e5a3c2385"

    response: Any = client.blocks.children.append(
        block_id=block_id,
        children=[
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Lacinato kale",
                            },
                        },
                    ],
                },
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "text": [
                        {
                            "type": "text",
                            "text": {
                                "content": (
                                    "Lacinato kale is a variety of kale with a long "
                                    "tradition in Italian cuisine, especially that of "
                                    "Tuscany. It is also known as Tuscan kale, Italian "
                                    "kale, dinosaur kale, kale, flat back kale, palm "
                                    "tree kale, or black Tuscan palm."
                                ),
                                "link": {
                                    "url": "https://en.wikipedia.org/wiki/Lacinato_kale",
                                },
                            },
                        },
                    ],
                },
            },
        ],
    )

    assert response["object"] == "list"

    # Check children blocks exists
    heading_2_block: Optional[dict] = None
    paragraph_block: Optional[dict] = None

    for result in response["results"]:
        if result["type"] == "heading_2" and "heading_2" in result:
            heading_2_block = result

        if result["type"] == "paragraph" and "paragraph" in result:
            paragraph_block = result

    assert heading_2_block is not None
    assert paragraph_block is not None


@pytest.mark.vcr()
def test_endpoint_blocks_children_list(client: "Client"):
    block_id = "69bf5c26-ff31-4d18-a331-c6d1746dec26"

    # Without kwargs
    response: Any = client.blocks.children.list(block_id=block_id)

    assert response["object"] == "list"
    assert response["results"]

    # With kwargs (page_size)
    response: Any = client.blocks.children.list(block_id=block_id, page_size=2)

    assert response["object"] == "list"
    assert len(response["results"]) == 2
