import os
# from filesplit.split import Split
from notion_client import Client
import io
import concurrent.futures

from typing import Tuple
from dotenv import load_dotenv
load_dotenv()

# Initialize the client
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
client = Client(auth=NOTION_TOKEN)


def main():
    file_waiting_for_upload_name = "test_file_large.txt"
    block_type = "file"
    # First create and send a file upload
    response = client.file_uploads.create(
        mode="multi_part", filename="test_file_large.txt", content_type="text/plain", number_of_parts=3
    )
    file_upload_id = response["id"]

    # initialize parts
    for part_number in range(1, 4):
        test_content_part = b"A" * (10 * 1024 * 1024)
        file_part = io.BytesIO(test_content_part)
        file_part.name = f"test_file_large.txt.sf-part{part_number}"

        client.file_uploads.send(
            file_upload_id=file_upload_id, file=file_part, part_number=str(part_number)
        )

    # complete the file upload
    response = client.file_uploads.complete(file_upload_id=file_upload_id)

    # Upload to the specified Notion database
    data_source_id = os.getenv("NOTION_DATA_SOURCE_ID", "")
    if response["status"] == "uploaded":
        print(f"File uploaded successfully: {file_waiting_for_upload_name}")
        upload_file_to_notion_data_source(
            file_waiting_for_upload_name, file_upload_id, block_type, data_source_id
        )
        print("File added to database successfully.")
    else:
        print(f"File added failed with status: {response['status']}")


def upload_file_to_notion_data_source(
    file_waiting_for_upload_name, file_upload_id, block_type, data_source_id
):
    """Uploads the file to a Notion database."""

    client.pages.create(
        parent={"data_source_id": data_source_id},
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
        children=[
            {
                "type": block_type,
                block_type: {
                    "type": "file_upload",
                    "file_upload": {"id": file_upload_id},
                },
            }
        ],
    )


if __name__ == "__main__":
    main()
