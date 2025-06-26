import os
from filesplit.split import Split
from notion_client import Client

import asyncio
import json


# Initialize the client
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
notion = Client(auth=NOTION_TOKEN)


async def main():

    file_waiting_for_upload_path = "examples/file_uploads/example.mkv"
    block_type = "video"

    # check file size <=20MB
    file_size = os.path.getsize(file_waiting_for_upload_path)
    if file_size <= 20 * 1024 * 1024:  # 20MB
        raise ValueError("File size exceeds 20MB limit for small file upload")

    # create a directory for the split files
    file_waiting_for_upload_name = os.path.basename(file_waiting_for_upload_path)
    file_name_without_extention, _ = os.path.splitext(
        file_waiting_for_upload_name
    )  # Remove file extension
    file_split_name = file_name_without_extention + "_split"
    output_dir = os.path.join(
        os.path.dirname(file_waiting_for_upload_path), file_split_name
    )
    os.makedirs(output_dir, exist_ok=True)  # create directory if it does not exist

    # split the file
    split = Split(file_waiting_for_upload_path, output_dir)
    split.bysize(size=10 * 1024 * 1024)  # Split by size, 10 MB chunks
    number_of_parts = file_size // (10 * 1024 * 1024) + (
        1 if file_size % (10 * 1024 * 1024) > 0 else 0
    )

    # Get the path list of split files
    split_files_path = os.listdir(output_dir)
    split_files_path.remove("manifest")  # Remove manifest file
    split_files_path = sorted(
        split_files_path, key=lambda x: int(x.split("_")[-1].split(".")[0])
    )  # Sort files by part number
    split_files_path = [
        os.path.join(output_dir, file) for file in split_files_path
    ]  # Get full paths

    # create file upload
    mime_type = "video/mp4"
    response = notion.file_uploads.create(
        mode="multi_part",
        filename=file_waiting_for_upload_name,
        content_type=mime_type,
        number_of_parts=number_of_parts,
    )
    file_upload_id = response["id"]

    # send file upload request
    for i, file_waiting_for_upload_path in enumerate(split_files_path):
        file_waiting_for_upload_name_split = os.path.basename(
            file_waiting_for_upload_path
        )
        print(
            f"Uploading part {i + 1}/{number_of_parts}: {file_waiting_for_upload_name_split}"
        )

        # Upload each chunk
        with open(file_waiting_for_upload_path, "rb") as f:
            response = notion.file_uploads.send(
                file_upload_id=file_upload_id,
                file=f,
                part_number=str(i + 1),
            )

    # complete the file upload
    response = notion.file_uploads.complete(file_upload_id=file_upload_id)

    # Upload to the specified Notion database
    database_id = os.getenv("NOTION_DATABASE_ID", "")
    if response["status"] == "uploaded":
        print(f"File uploaded successfully: {file_waiting_for_upload_name}")
        upload_file_to_notion_database(
            file_waiting_for_upload_name, file_upload_id, block_type, database_id
        )
        print("File added to database successfully.")
    else:
        print(f"File added failed with status: {response['status']}")


def upload_file_to_notion_database(
    file_waiting_for_upload_name, file_upload_id, block_type, database_id
):
    """Uploads the file to a Notion database."""

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
    asyncio.run(main())
