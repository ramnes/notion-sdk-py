import os
import time

from notion_client import Client
from notion_client.helpers import is_full_page, iterate_paginated_api

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    pass
else:
    load_dotenv()

NOTION_KEY = os.getenv("NOTION_KEY", "")
SENDGRID_KEY = os.getenv("SENDGRID_KEY", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")
EMAIL_TO_FIELD = os.getenv("EMAIL_TO_FIELD", "")
EMAIL_FROM_FIELD = os.getenv("EMAIL_FROM_FIELD", "")

while NOTION_KEY == "":
    NOTION_KEY = input("Enter your Notion integration token: ").strip()

while NOTION_DATABASE_ID == "":
    NOTION_DATABASE_ID = input("Enter the Notion database ID: ").strip()

notion = Client(auth=NOTION_KEY)

task_page_id_to_status_map: dict[str, str] = {}


def get_tasks_from_notion_database():
    database = notion.databases.retrieve(database_id=NOTION_DATABASE_ID)
    data_sources = database.get("data_sources", [])
    if not data_sources:
        print("No data sources found on this database.")
        return []

    ds_id = data_sources[0]["id"]
    pages = list(
        iterate_paginated_api(notion.data_sources.query, data_source_id=ds_id)
    )
    print(f"{len(pages)} pages successfully fetched.")

    tasks = []
    for page in pages:
        page_id = page["id"]
        if not is_full_page(page):
            print(f"Page {page_id} is not a full page.")
            continue

        status_property_id = page["properties"]["Status"]["id"]
        property_result = notion.pages.properties.retrieve(
            page_id=page_id, property_id=status_property_id
        )
        status = get_status_value(property_result)

        title_property_id = page["properties"]["Name"]["id"]
        title_result = notion.pages.properties.retrieve(
            page_id=page_id, property_id=title_property_id
        )
        title = get_title_value(title_result)

        tasks.append({"page_id": page_id, "status": status, "title": title})

    return tasks


def get_status_value(property_result):
    if isinstance(property_result, list):
        item = property_result[0] if property_result else {}
    else:
        item = property_result

    if item.get("type") == "select":
        select = item.get("select")
        return select.get("name", "No Status") if select else "No Status"
    return "No Status"


def get_title_value(property_result):
    if isinstance(property_result, list):
        item = property_result[0] if property_result else {}
    else:
        item = property_result

    if item.get("type") == "title":
        title = item.get("title", {})
        return title.get("plain_text", "No Title")
    return "No Title"


def find_updated_tasks(current_tasks):
    updated = []
    for task in current_tasks:
        previous_status = task_page_id_to_status_map.get(task["page_id"])
        if previous_status is not None and task["status"] != previous_status:
            updated.append(task)
    return updated


def send_update_email(task):
    message = (
        f'Status of Notion task ("{task["title"]}") '
        f'has been updated to "{task["status"]}".'
    )
    print(message)

    if not SENDGRID_KEY or not EMAIL_TO_FIELD or not EMAIL_FROM_FIELD:
        print("SendGrid not configured. Skipping email.")
        return

    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        sg = SendGridAPIClient(SENDGRID_KEY)
        mail = Mail(
            from_email=EMAIL_FROM_FIELD,
            to_emails=EMAIL_TO_FIELD,
            subject="Notion Task Status Updated",
            plain_text_content=message,
        )
        sg.send(mail)
        print(f"Email sent to {EMAIL_TO_FIELD} from {EMAIL_FROM_FIELD}")
    except ImportError:
        print("sendgrid package not installed. Run: pip install sendgrid")
    except Exception as e:
        print(f"Failed to send email: {e}")


def main():
    print("Initializing task status map...")
    current_tasks = get_tasks_from_notion_database()
    for task in current_tasks:
        task_page_id_to_status_map[task["page_id"]] = task["status"]
    print(f"Tracking {len(current_tasks)} tasks. Polling every 5 seconds...\n")

    while True:
        time.sleep(5)
        print("\nFetching tasks from Notion DB...")
        current_tasks = get_tasks_from_notion_database()
        updated_tasks = find_updated_tasks(current_tasks)
        print(f"Found {len(updated_tasks)} updated tasks.")

        for task in updated_tasks:
            task_page_id_to_status_map[task["page_id"]] = task["status"]
            send_update_email(task)


if __name__ == "__main__":
    main()
