import os
from pathlib import Path

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
- File upload guide: https://developers.notion.com/docs/uploading-small-files
- Create file upload API: https://developers.notion.com/reference/create-a-file-upload
"""


def create_file_upload():
    return notion.file_uploads.create(
        mode="single_part",
    )


def send_file_upload(file_upload_id, file_path):
    with open(file_path, "rb") as file:
        return notion.file_uploads.send(
            file_upload_id=file_upload_id,
            file=file,
        )


def append_block_children(block_id, file_upload_id):
    return notion.blocks.children.append(
        block_id=block_id,
        children=[
            {
                "type": "image",
                "image": {
                    "type": "file_upload",
                    "file_upload": {
                        "id": file_upload_id,
                    },
                },
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "This is a test",
                            },
                        },
                    ],
                },
            },
        ],
    )


def main():
    file_upload = create_file_upload()
    print("Created file upload with ID:", file_upload["id"])

    script_dir = Path(__file__).parent
    image_path = script_dir.parent / "assets" / "page_id.png"

    file_upload = send_file_upload(file_upload["id"], str(image_path))
    print("Uploaded page_id.png to file upload; status is now:", file_upload["status"])

    # Append an image block with the file upload from above, and a text block,
    # to the configured page.
    new_blocks = append_block_children(page_id, file_upload["id"])
    new_block_ids = [block["id"] for block in new_blocks["results"]]
    print("Appended block children; new list of block children is:", new_block_ids)

    # Create a comment on the text block with the same image by providing
    # the same file upload ID. Also use a custom display name.
    comment = notion.comments.create(
        parent={
            "type": "block_id",
            "block_id": new_block_ids[1],
        },
        rich_text=[
            {
                "type": "text",
                "text": {"content": "I'm commenting on this block with an image:"},
            },
        ],
        attachments=[
            {
                "type": "file_upload",
                "file_upload_id": file_upload["id"],
            },
        ],
        display_name={
            "type": "custom",
            "custom": {
                "name": "Notion test auto commenter",
            },
        },
    )

    print("Comment ID:", comment["id"])

    if comment["object"] == "comment":
        print("Discussion ID:", comment["discussion_id"])
        print("Comment parent:", comment["parent"])
        print("Comment created by:", comment["created_by"])
        print("Comment display name:", comment["display_name"])
    else:
        print("No read access to comment object")

    print("Done! Image & comment added to page:", page_id)


if __name__ == "__main__":
    main()
