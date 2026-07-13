import os

from notion_client import Client
from notion_client.helpers import iterate_paginated_api

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    pass
else:
    load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID", "")

while NOTION_API_KEY == "":
    NOTION_API_KEY = input("Enter your Notion integration token: ").strip()

while NOTION_PAGE_ID == "":
    NOTION_PAGE_ID = input("Enter the Notion page ID: ").strip()

notion = Client(auth=NOTION_API_KEY)


def get_plain_text_from_rich_text(rich_text):
    return "".join(t.get("plain_text", "") for t in rich_text)


def get_media_source_text(block):
    block_type = block["type"]
    block_data = block[block_type]

    if "external" in block_data:
        source = block_data["external"]["url"]
    elif "file" in block_data:
        source = block_data["file"]["url"]
    elif "url" in block_data:
        source = block_data["url"]
    else:
        source = f"[Missing case for media block types]: {block_type}"

    if block_data.get("caption"):
        caption = get_plain_text_from_rich_text(block_data["caption"])
        return f"{caption}: {source}"
    return source


def get_text_from_block(block):
    block_type = block["type"]
    block_data = block[block_type]

    if "rich_text" in block_data:
        text = get_plain_text_from_rich_text(block_data["rich_text"])
    else:
        if block_type == "unsupported":
            text = "[Unsupported block type]"
        elif block_type == "bookmark":
            text = block_data["url"]
        elif block_type == "child_database":
            text = block_data["title"]
        elif block_type == "child_page":
            text = block_data["title"]
        elif block_type in ("embed", "video", "file", "image", "pdf"):
            text = get_media_source_text(block)
        elif block_type == "equation":
            text = block_data["expression"]
        elif block_type == "link_preview":
            text = block_data["url"]
        elif block_type == "synced_block":
            synced_from = block_data.get("synced_from")
            if synced_from:
                source_type = synced_from["type"]
                text = f"This block is synced with a block with the following ID: {synced_from[source_type]}"
            else:
                text = "Source sync block that another block is synced with."
        elif block_type == "table":
            text = f"Table width: {block_data['table_width']}"
        elif block_type == "table_of_contents":
            text = f"ToC color: {block_data['color']}"
        elif block_type in ("breadcrumb", "column_list", "divider"):
            text = "No text available"
        else:
            text = "[Needs case added]"

    if block.get("has_children"):
        text = f"{text} (Has children)"

    return f"{block_type}: {text}"


def retrieve_block_children(page_id):
    print("Retrieving blocks...")
    blocks = []
    for block in iterate_paginated_api(notion.blocks.children.list, block_id=page_id):
        blocks.append(block)
    return blocks


def print_block_text(blocks):
    print("Displaying blocks:")
    for i, block in enumerate(blocks, 1):
        text = get_text_from_block(block)
        print(f"{i}. {text}")


def main():
    blocks = retrieve_block_children(NOTION_PAGE_ID)
    print_block_text(blocks)


if __name__ == "__main__":
    main()
