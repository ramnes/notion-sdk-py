import os
import re
import time

import requests
from notion_client import Client

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    pass
else:
    load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO_OWNER = os.getenv("GITHUB_REPO_OWNER", "")
GITHUB_REPO_NAME = os.getenv("GITHUB_REPO_NAME", "")

UPDATE_STATUS = (
    os.getenv("UPDATE_STATUS_IN_NOTION_DB", "").strip().lower() == "true"
)
STATUS_PROPERTY_NAME = os.getenv("STATUS_PROPERTY_NAME", "").strip()

if UPDATE_STATUS and not STATUS_PROPERTY_NAME:
    raise ValueError(
        "STATUS_PROPERTY_NAME is required when UPDATE_STATUS_IN_NOTION_DB=true"
    )

while NOTION_API_KEY == "":
    NOTION_API_KEY = input("Enter your Notion integration token: ").strip()
while GITHUB_TOKEN == "":
    GITHUB_TOKEN = input("Enter your GitHub personal access token: ").strip()
while GITHUB_REPO_OWNER == "":
    GITHUB_REPO_OWNER = input("Enter the GitHub repo owner: ").strip()
while GITHUB_REPO_NAME == "":
    GITHUB_REPO_NAME = input("Enter the GitHub repo name: ").strip()

notion = Client(auth=NOTION_API_KEY)
GITHUB_API_BASE = "https://api.github.com"
OPERATION_BATCH_SIZE = 10

NOTION_URL_RE = re.compile(
    r"https://www\.notion\.so/([A-Za-z0-9]+(-[A-Za-z0-9]+)+)$"
)


def has_integration_commented_on_page(page_id):
    bot = notion.users.me()
    cursor = None
    while True:
        comments = notion.comments.list(
            block_id=page_id,
            start_cursor=cursor,
            page_size=100,
        )
        for comment in comments.get("results", []):
            if comment["created_by"]["id"] == bot["id"]:
                return True
        if not comments.get("has_more"):
            break
        cursor = comments.get("next_cursor")
    return False


def get_github_prs():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    pull_requests = []
    page = 1
    while True:
        url = (
            f"{GITHUB_API_BASE}/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/pulls"
            f"?state=all&per_page=100&page={page}"
        )
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        for pr in data:
            body = pr.get("body") or ""
            match = NOTION_URL_RE.search(body)
            if match and pr.get("state") == "closed":
                page_id = match.group(0).split("-")[-1].replace("-", "")
                merged = pr.get("merged_at") is not None
                status = "Closed - Merged" if merged else "Closed - Not Merged"
                content = " has been merged!" if merged else " was closed but not merged!"
                pull_requests.append({
                    "task_link": match.group(0),
                    "page_id": page_id,
                    "pr_link": pr["html_url"],
                    "pr_status": status,
                    "comment_content": content,
                })
        page += 1
        if len(data) < 100:
            break
    print(f"Fetched {len(pull_requests)} closed PR(s) from GitHub.")
    return pull_requests


def update_pages(pages_to_update):
    if not pages_to_update:
        print("Notion Tasks are already up-to-date")
        return

    for i in range(0, len(pages_to_update), OPERATION_BATCH_SIZE):
        batch = pages_to_update[i:i + OPERATION_BATCH_SIZE]
        for pr in batch:
            if UPDATE_STATUS:
                notion.pages.update(
                    page_id=pr["page_id"],
                    properties={
                        STATUS_PROPERTY_NAME: {
                            "status": {"name": pr["pr_status"]}
                        }
                    },
                )
            notion.comments.create(
                parent={"page_id": pr["page_id"]},
                rich_text=[
                    {
                        "type": "text",
                        "text": {
                            "content": "Your PR",
                            "link": {"url": pr["pr_link"]},
                        },
                        "annotations": {"bold": True},
                    },
                    {
                        "type": "text",
                        "text": {"content": pr["comment_content"]},
                    },
                ],
            )
        time.sleep(0.5)

    print(f"Successfully updated {len(pages_to_update)} task(s) in Notion")


def main():
    print("Fetching PRs from GitHub repository...")
    prs = get_github_prs()

    prs_to_update = []
    for pr in prs:
        if not has_integration_commented_on_page(pr["page_id"]):
            prs_to_update.append(pr)

    update_pages(prs_to_update)


if __name__ == "__main__":
    main()
