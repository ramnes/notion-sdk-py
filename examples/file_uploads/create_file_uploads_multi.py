import os
from filesplit.split import Split
from notion_client import Client

import concurrent.futures

from typing import Tuple

# Initialize the client
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
notion = Client(auth=NOTION_TOKEN)


def main():
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

    # Get the path list of split files
    split_files_path = os.listdir(output_dir)
    split_files_path.remove("manifest")  # Remove manifest file
    split_files_path = sorted(
        split_files_path, key=lambda x: int(x.split("_")[-1].split(".")[0])
    )  # Sort files by part number
    split_files_path = [
        os.path.join(output_dir, file) for file in split_files_path
    ]  # Get full paths
    number_of_parts = len(split_files_path)  # Number of parts created

    # create file upload
    mime_type = "video/mp4"
    response = notion.file_uploads.create(
        mode="multi_part",
        filename=file_waiting_for_upload_name,
        content_type=mime_type,
        number_of_parts=number_of_parts,
    )
    file_upload_id = response["id"]

    # send file upload request (parallel upload)
    print(f"Starting parallel upload of {number_of_parts} parts...")

    def upload_part(part_info: Tuple):
        """Upload a single part of the file"""
        part_index, file_path = part_info
        part_number = part_index + 1

        print(f"Uploading part {part_number}/{number_of_parts}")

        try:
            with open(file_path, "rb") as f:
                notion.file_uploads.send(
                    file_upload_id=file_upload_id,
                    file=f,
                    part_number=str(part_number),
                )
            print(f"Part {part_number} uploaded successfully")
            return part_number, True, None
        except Exception as e:
            print(f"Part {part_number} failed: {e}")
            return part_number, False, e

    # Create list of part information for parallel processing
    part_infos = list(enumerate(split_files_path))

    # Use ThreadPoolExecutor for parallel uploads
    # Limit concurrent uploads to avoid hitting rate limits
    max_concurrent_uploads = min(5, number_of_parts)  # Max 5 concurrent uploads

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=max_concurrent_uploads
    ) as executor:
        # Submit all upload tasks
        future_to_part = {
            executor.submit(upload_part, part_info): part_info[0] + 1
            for part_info in part_infos
        }

        # Collect results
        successful_parts = []
        failed_parts = []

        for future in concurrent.futures.as_completed(future_to_part):
            part_number = future_to_part[future]
            try:
                part_num, success, error = future.result()
                if success:
                    successful_parts.append(part_num)
                else:
                    failed_parts.append((part_num, error))
            except Exception as exc:
                failed_parts.append((part_number, exc))
                print(f"Part {part_number} generated an exception: {exc}")

    # Check if all parts uploaded successfully
    if failed_parts:
        print(f"\n Upload failed! {len(failed_parts)} parts failed:")
        for part_num, error in failed_parts:
            print(f"Part {part_num}: {error}")
        return

    print(f"\n All {len(successful_parts)} parts uploaded successfully!")

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

    # Resolve a data source ID from a database_id (or use as-is if already a
    # data_source_id). This keeps backward compatibility with existing env vars.
    ds_parent = {"type": "data_source_id", "data_source_id": database_id}
    try:
        db = notion.databases.retrieve(database_id)
        if db.get("data_sources"):
            ds_parent = {
                "type": "data_source_id",
                "data_source_id": db["data_sources"][0]["id"],
            }
    except Exception:
        pass

    notion.pages.create(
        parent=ds_parent,
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
