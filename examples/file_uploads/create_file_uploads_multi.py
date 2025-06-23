import os
import sys

from notion_client import Client
from notion_client.helpers import get_id

# from notion_client.helpers import guess_content_type
from notion_mime_detector import NotionMIMETypeDetector

from examples.file_uploads.split_file import split_file_async

# import httpx

import asyncio

from dotenv import load_dotenv

if os.getenv("ENV") != "production":
    load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")

while NOTION_TOKEN == "":
    print("NOTION_TOKEN not found.")
    NOTION_TOKEN = input("Enter your integration token: ").strip()

# Initialize the client
notion = Client(auth=NOTION_TOKEN)

detector = NotionMIMETypeDetector()


async def main():

    file_waiting_for_upload_path = r"examples\file_uploads\config.mkv"
    file_waiting_for_upload_name = os.path.basename(file_waiting_for_upload_path)

    # Check if the file is supported by the Notion API.
    is_supported = detector.is_supported_by_notion(file_waiting_for_upload_name)
    if is_supported:
        mime_type, _ = detector.guess_type(file_waiting_for_upload_name)
    else:
        raise ValueError(
            f"File type not supported by Notion: {file_waiting_for_upload_name}"
        )

    print(f"Preparing to upload file: {file_waiting_for_upload_name}")

    # check file size <=20MB
    file_size = os.path.getsize(file_waiting_for_upload_path)
    if file_size <= 20 * 1024 * 1024:  # 20MB
        raise ValueError("File size exceeds 20MB limit for small file upload")

    print(f"Guessed content type: {mime_type}")

    output_file_names = await split_file_async(
        file_waiting_for_upload_path,
        1024 * 1024 * 10  # 10 MB
    )

    # create file upload
    number_of_parts = len(output_file_names)
    response = notion.file_uploads.create(
        mode="multi_part",
        filename=file_waiting_for_upload_name,
        content_type = mime_type,
        number_of_parts = number_of_parts,
    )
    file_upload_id = response["id"]
    print(f"File upload created with ID: {file_upload_id}")

    # send file upload request
    for i, file_waiting_for_upload_path in enumerate(output_file_names):
        file_waiting_for_upload_name_split = os.path.basename(file_waiting_for_upload_path)
        print(f"Uploading part {i + 1}/{number_of_parts}: {file_waiting_for_upload_name_split}")

        # Upload each chunk
        with open(file_waiting_for_upload_path, "rb") as f:
            response = notion.file_uploads.send(
                file_upload_id=file_upload_id,
                file=(file_waiting_for_upload_name, f, mime_type),
                part_number=i + 1,
            )

    print(f"Part {i + 1} upload response: {response}")

    # complete the file upload
    response = notion.file_uploads.complete(file_upload_id=file_upload_id)
    print(f"File upload completed with response: {response}")

    # Upload to the specified Notion database
    print(type(response))
    print(response)
    print(f"最终状态: {response["status"]}")
    if response["status"] == "uploaded":
        upload_file_to_notion_database(file_waiting_for_upload_name, file_upload_id, "video")
    else:
        print(f"File upload failed with status: {response['status']}")

def upload_file_to_notion_database(file_waiting_for_upload_name, file_upload_id, block_type):
    """Uploads the file to a Notion database."""
    database_id = os.getenv("NOTION_DATABASE_ID", "")
    notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Name": {
                "title": [{"text": {"content": file_waiting_for_upload_name}}]
            },
            "Files": {
                "type": "files",
                "files": [
                    {
                        "type": "file_upload",
                        "file_upload": {"id": file_upload_id},
                    },
                ],
            },
        },
        children=[
            {
                "type": block_type,
                block_type: {
                    "type": "file_upload",
                    "file_upload": {
                        "id": file_upload_id
                    }
                }
            }

        ]

    )
    print("File added to database successfully.")



if __name__ == "__main__":
    asyncio.run(main())
