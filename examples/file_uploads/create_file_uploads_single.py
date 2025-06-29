import os

from notion_client import Client

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")

while NOTION_TOKEN == "":
    print("NOTION_TOKEN not found.")
    NOTION_TOKEN = input("Enter your integration token: ").strip()

# Initialize the client
notion = Client(auth=NOTION_TOKEN)


def main():
    file_waiting_for_upload_path = "examples/file_uploads/example.jpg"
    file_waiting_for_upload_name = os.path.basename(file_waiting_for_upload_path)

    # check file size <=20MB
    file_size = os.path.getsize(file_waiting_for_upload_path)
    if file_size > 20 * 1024 * 1024:  # 20MB
        raise ValueError("File size exceeds 20MB limit for small file upload")

    # create file upload
    response = notion.file_uploads.create(
        mode="single_part",
        filename=file_waiting_for_upload_name,
        # content_type = content_type,
    )
    file_upload_id = response["id"]
    print(f"File upload created with ID: {file_upload_id}")

    # uplod files send
    with open(file_waiting_for_upload_path, "rb") as f:
        response = notion.file_uploads.send(
            file_upload_id=file_upload_id,
            file=f,
        )

    # Upload to the specified Notion database
    database_id = os.getenv("NOTION_DATABASE_ID", "")
    if response["status"] == "uploaded":
        print(f"File uploaded successfully.: {file_waiting_for_upload_name}")
        upload_file_to_notion_database(
            file_waiting_for_upload_name, file_upload_id, database_id
        )
        print("File added to database successfully.")
    else:
        print(f"File upload failed with status: {response['status']}")


def upload_file_to_notion_database(
    file_waiting_for_upload_name, file_upload_id, database_id
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
    )


if __name__ == "__main__":
    main()
