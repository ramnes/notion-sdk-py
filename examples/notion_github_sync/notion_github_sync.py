import os
import time

import requests
from notion_client import Client
from notion_client.helpers import is_full_database

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    pass
else:
    load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO_OWNER = os.getenv("GITHUB_REPO_OWNER", "")
GITHUB_REPO_NAME = os.getenv("GITHUB_REPO_NAME", "")

while NOTION_API_KEY == "":
    NOTION_API_KEY = input("Enter your Notion integration token: ").strip()
while NOTION_DATABASE_ID == "":
    NOTION_DATABASE_ID = input("Enter the Notion database ID: ").strip()
while GITHUB_TOKEN == "":
    GITHUB_TOKEN = input("Enter your GitHub personal access token: ").strip()
while GITHUB_REPO_OWNER == "":
    GITHUB_REPO_OWNER = input("Enter the GitHub repo owner: ").strip()
while GITHUB_REPO_NAME == "":
    GITHUB_REPO_NAME = input("Enter the GitHub repo name: ").strip()

notion = Client(auth=NOTION_API_KEY)
GITHUB_API_BASE = "https://api.github.com"
OPERATION_BATCH_SIZE = 10


def get_issues_from_notion_database():
    database = notion.databases.retrieve(database_id=NOTION_DATABASE_ID)
    if not is_full_database(database):
        print(f"No read permissions on database: {NOTION_DATABASE_ID}")
        return {}

    data_source_id = database["data_sources"][0]["id"]
    print(f"Querying data source: {data_source_id}")

    issue_map = {}
    cursor = None
    while True:
        response = notion.data_sources.query(
            data_source_id=data_source_id,
            start_cursor=cursor,
            page_size=100,
        )
        for page in response.get("results", []):
            issue_number = page["properties"]["Issue Number"]["id"]
            prop_result = notion.pages.properties.retrieve(
                page_id=page["id"],
                property_id=issue_number,
            )
            if "number" in prop_result and prop_result["number"] is not None:
                issue_map[prop_result["number"]] = page["id"]

        if not response.get("has_more"):
            break
        cursor = response.get("next_cursor")

    print(f"Found {len(issue_map)} existing issues in Notion database.")
    return issue_map


def get_github_issues():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    issues = []
    page = 1
    while True:
        url = (
            f"{GITHUB_API_BASE}/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/issues"
            f"?state=all&per_page=100&page={page}"
        )
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        for item in data:
            if "pull_request" not in item:
                issues.append({
                    "number": item["number"],
                    "title": item["title"],
                    "state": item["state"],
                    "comment_count": item["comments"],
                    "url": item["html_url"],
                })
        page += 1
        if len(data) < 100:
            break
    print(f"Fetched {len(issues)} issues from GitHub.")
    return issues


def get_notion_operations(issues, existing_issue_map):
    to_create = []
    to_update = []
    for issue in issues:
        page_id = existing_issue_map.get(issue["number"])
        if page_id:
            to_update.append({**issue, "page_id": page_id})
        else:
            to_create.append(issue)
    return to_create, to_update


def get_properties_from_issue(issue):
    return {
        "Name": {
            "title": [{"type": "text", "text": {"content": issue["title"]}}],
        },
        "Issue Number": {"number": issue["number"]},
        "State": {"select": {"name": issue["state"]}},
        "Number of Comments": {"number": issue["comment_count"]},
        "Issue URL": {"url": issue["url"]},
    }


def create_pages(pages_to_create):
    if not pages_to_create:
        return
    for i in range(0, len(pages_to_create), OPERATION_BATCH_SIZE):
        batch = pages_to_create[i:i + OPERATION_BATCH_SIZE]
        for issue in batch:
            notion.pages.create(
                parent={"database_id": NOTION_DATABASE_ID},
                properties=get_properties_from_issue(issue),
            )
        print(f"Created batch of {len(batch)} pages.")
        time.sleep(0.5)


def update_pages(pages_to_update):
    if not pages_to_update:
        return
    for i in range(0, len(pages_to_update), OPERATION_BATCH_SIZE):
        batch = pages_to_update[i:i + OPERATION_BATCH_SIZE]
        for issue in batch:
            notion.pages.update(
                page_id=issue["page_id"],
                properties=get_properties_from_issue(issue),
            )
        print(f"Updated batch of {len(batch)} pages.")
        time.sleep(0.5)


def main():
    print("Syncing GitHub issues to Notion database...")
    existing_issue_map = get_issues_from_notion_database()
    issues = get_github_issues()
    to_create, to_update = get_notion_operations(issues, existing_issue_map)

    print(f"\n{len(to_create)} new issues to add to Notion.")
    create_pages(to_create)

    print(f"\n{len(to_update)} issues to update in Notion.")
    update_pages(to_update)

    print("\nNotion database is synced with GitHub.")


if __name__ == "__main__":
    main()
