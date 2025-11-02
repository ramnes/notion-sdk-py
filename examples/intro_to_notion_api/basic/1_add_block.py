import json
import os

from notion_client import Client

try:
    from dotenv import load_dotenv

    load_dotenv()
except ModuleNotFoundError:
    pass

page_id = os.getenv("NOTION_PAGE_ID")
api_key = os.getenv("NOTION_API_KEY")

notion = Client(auth=api_key)

# ---------------------------------------------------------------------------

"""
Resources:
- Appending block children endpoint (notion.blocks.children.append(): https://developers.notion.com/reference/patch-block-children)
- Working with page content guide: https://developers.notion.com/docs/working-with-page-content
"""


def main():
    block_id = page_id  # Blocks can be appended to other blocks *or* pages. Therefore, a page ID can be used for the block_id parameter
    new_heading_response = notion.blocks.children.append(
        block_id=block_id,
        # Pass an array of blocks to append to the page: https://developers.notion.com/reference/block#block-type-objects
        children=[
            {
                "heading_2": {
                    "rich_text": [
                        {
                            "text": {
                                "content": "Types of kale",  # This is the text that will be displayed in Notion
                            },
                        },
                    ],
                },
            },
        ],
    )

    # Print the new block(s) response
    print(json.dumps(new_heading_response, indent=2))


if __name__ == "__main__":
    main()
