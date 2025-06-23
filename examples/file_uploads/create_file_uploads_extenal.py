import os
import sys

from notion_client import Client
from notion_client.helpers import get_id

# from notion_client.helpers import guess_content_type
from notion_mime_detector import NotionMIMETypeDetector

# import httpx

import time

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


def _wait_for_upload_completion(
    file_upload_id: str, poll_interval: int = 5, max_wait_time: int = 300
) -> str:
    """
    Wait for file upload/import to complete.

    Args:
        file_upload_id: The file upload ID.
        poll_interval: Polling interval in seconds.
        max_wait_time: Maximum wait time in seconds.

    Returns:
        file_upload_id: The file ID after successful completion.
    """
    start_time = time.time()

    while time.time() - start_time < max_wait_time:
        upload_status = notion.file_uploads.retrieve(file_upload_id=file_upload_id)
        status = upload_status["status"]

        print(f"Current status: {status}")

        if status == "uploaded":
            print("File uploaded successfully!")
            if "filename" in upload_status:
                print(f"Filename: {upload_status['filename']}")
            if "content_type" in upload_status:
                print(f"Content Type: {upload_status['content_type']}")
            if "content_length" in upload_status:
                print(f"File Size: {upload_status['content_length']} bytes")
            return file_upload_id

        elif status == "failed":
            error_msg = "File upload failed"
            if "file_import_result" in upload_status:
                import_result = upload_status["file_import_result"]
                if import_result.get("type") == "error" and "error" in import_result:
                    error_detail = import_result["error"]
                    error_msg += f": {error_detail.get('message', 'Unknown error')}"
            raise Exception(error_msg)

        elif status == "pending":
            print(f"File is processing, retrying in {poll_interval} seconds...")
            time.sleep(poll_interval)

        else:
            print(f"Unknown status: {status}, continuing to wait...")
            time.sleep(poll_interval)

    raise TimeoutError(f"File upload timed out ({max_wait_time} seconds)")


def main():

    file_waiting_for_upload_url = (
        "https://cn.bing.com/th?id=OHR.MonaValePool_ZH-CN7968271596_UHD.jpg"
    )
    file_waiting_for_upload_name = "bing.png"
    # create file upload
    response = notion.file_uploads.create(
        mode="external_url",
        filename=file_waiting_for_upload_name,
        external_url=file_waiting_for_upload_url,
    )
    file_upload_id = response["id"]
    print(f"File upload created with ID: {file_upload_id}")

    # Wait for file upload to complete
    _wait_for_upload_completion(file_upload_id)

    # Upload to the specified Notion database
    database_id = os.getenv("NOTION_DATABASE_ID", "")

    notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Name": {"title": [{"text": {"content": file_waiting_for_upload_name}}]},
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


if __name__ == "__main__":
    main()
