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
- Rich text options: https://developers.notion.com/reference/rich-text
- Working with page content guide: https://developers.notion.com/docs/working-with-page-content
"""


def main():
    block_id = page_id  # Blocks can be appended to other blocks *or* pages. Therefore, a page ID can be used for the block_id parameter
    styled_link_text_response = notion.blocks.children.append(
        block_id=block_id,
        children=[
            {
                "heading_3": {
                    "rich_text": [
                        {
                            "text": {
                                "content": "Tuscan  kale",
                            },
                        },
                    ],
                },
            },
            {
                "paragraph": {
                    "rich_text": [
                        {
                            "text": {
                                # Paragraph text
                                "content": "Tuscan  kale is a variety of kale with a long tradition in Italian cuisine, especially that of Tuscany. It is also known as Tuscan kale, Italian kale, dinosaur kale, kale, flat back kale, palm tree kale, or black Tuscan palm.",
                                "link": {
                                    # Paragraph link
                                    "url": "https://en.wikipedia.org/wiki/Kale",
                                },
                            },
                            "annotations": {
                                # Paragraph styles
                                "bold": True,
                                "italic": True,
                                "strikethrough": True,
                                "underline": True,
                                "color": "green",
                            },
                        },
                    ],
                },
            },
        ],
    )

    # Print the new block(s) response
    print(json.dumps(styled_link_text_response, indent=2))


if __name__ == "__main__":
    main()
