import os
import sys

from notion_client import Client
from notion_client.helpers import get_id

# from notion_client.helpers import guess_content_type
from notion_mime_detector import NotionMIMETypeDetector

# import httpx

import requests

from dotenv import load_dotenv

# 仅本地开发时加载 .env 文件（Docker 环境会跳过）
if os.getenv("ENV") != "production":
    load_dotenv()  # 默认加载 .env 文件

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")

while NOTION_TOKEN == "":
    print("NOTION_TOKEN not found.")
    NOTION_TOKEN = input("Enter your integration token: ").strip()

# Initialize the client
notion = Client(auth=NOTION_TOKEN)

detector = NotionMIMETypeDetector()


def main():

    file_waiting_for_upload_path = r"examples\file_uploads\example.png"
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
    if file_size > 20 * 1024 * 1024:  # 20MB
        raise ValueError("File size exceeds 20MB limit for small file upload")

    print(f"Guessed content type: {mime_type}")

    # create file upload
    response = notion.file_uploads.create(
        mode="single_part",
        filename=file_waiting_for_upload_name,
        # content_type = content_type,
        # number_of_parts = 1,
    )
    file_upload_id = response["id"]
    print(f"File upload created with ID: {file_upload_id}")

    # uplod files send
    with open(file_waiting_for_upload_path, "rb") as f:
        response = notion.file_uploads.send(
            file_upload_id=file_upload_id,
            file=(file_waiting_for_upload_name, f, mime_type),
        )

    # Upload to the specified Notion database
    database_id = os.getenv("NOTION_DATABASE_ID", "")
    print(type(response))
    print(response)
    print(f"最终状态: {response["status"]}")
    if response["status"] == "uploaded":
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
        )
        print("File added to database successfully.")
    else:
        print(f"File upload failed with status: {response['status']}")


if __name__ == "__main__":
    main()
