import os
import time
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

# Initialize the client
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
notion = Client(auth=NOTION_TOKEN)


def _wait_for_upload_completion(
    file_upload_id: str, poll_interval: int = 5, max_wait_time: int = 300
):
    """
    Wait for file upload/import to complete.

    Args:
        file_upload_id: The file upload ID.
        poll_interval: Polling interval in seconds.
        max_wait_time: Maximum wait time in seconds.
    """
    start_time = time.monotonic()

    while time.monotonic() - start_time < max_wait_time:
        upload_status = notion.file_uploads.retrieve(file_upload_id=file_upload_id)
        status = upload_status["status"]

        print(f"Current status: {status}")

        if status == "uploaded":
            print("File uploaded successfully!")
            return

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
        "https://www.bing.com/th?id=OHR.MonaValePool_ZH-CN7968271596_UHD.jpg"
    )
    file_waiting_for_upload_name = "bing.png"

    # create file upload
    response = notion.file_uploads.create(
        mode="external_url",
        filename=file_waiting_for_upload_name,
        external_url=file_waiting_for_upload_url,
    )
    file_upload_id = response["id"]

    # Wait for file upload to complete
    _wait_for_upload_completion(file_upload_id)

    # Upload to the specified Notion database
    database_id = os.getenv("NOTION_DATABASE_ID", "")

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
    )
    print("File added to database successfully.")


if __name__ == "__main__":
    main()
