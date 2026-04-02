import asyncio
import hashlib
import json
import logging
import os
from typing import Dict
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from github import Github
import httpx
from markdownify import markdownify as md

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

# Constants
NOTION_BASE_URL = "https://developers.notion.com"
NOTION_CHANGELOG_URL = f"{NOTION_BASE_URL}/page/changelog"
DATA_FILE = ".github/scripts/known_entries.json"
GITHUB_REPOSITORY = "ramnes/notion-sdk-py"


async def fetch_changelog() -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(NOTION_CHANGELOG_URL)
        response.raise_for_status()
        return response.text


def resolve_relative_urls(element):
    """Resolve relative URLs to absolute URLs."""
    for tag in element.find_all(href=True):
        tag["href"] = urljoin(NOTION_BASE_URL, tag["href"])
    for tag in element.find_all(src=True):
        tag["src"] = urljoin(NOTION_BASE_URL, tag["src"])


def extract_entries(html) -> Dict[str, Dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")

    # Each changelog entry is a div with class "update-container"
    entries = soup.find_all("div", class_="update-container")
    parsed_data = {}

    for entry in entries:
        # The entry-level anchor id is on the container div itself
        section_id = entry.get("id")
        if section_id is None:
            continue

        # Date is in a div with data-component-part="update-label"
        label = entry.find(attrs={"data-component-part": "update-label"})
        if label is None:
            continue
        date_text = label.text.strip()

        # Content is in a div with data-component-part="update-content"
        content_div = entry.find(attrs={"data-component-part": "update-content"})
        if content_div is None:
            continue

        content = content_div.text.strip()

        # Remove anchor link icons (zero-width space links on headings)
        for anchor_div in content_div.find_all("div", class_="absolute"):
            anchor_div.decompose()

        resolve_relative_urls(content_div)
        content_md = [md(str(content_div))]

        md5_hash = hashlib.md5(content.encode()).hexdigest()
        parsed_data[md5_hash] = {
            "section_id": section_id,
            "title": date_text,
            "content_md": content_md,
        }

    return parsed_data


def read_known_entries() -> Dict[str, Dict[str, str]]:
    if not os.path.exists(DATA_FILE):
        return dict()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_known_entries(entries: Dict[str, Dict[str, str]]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)
        f.write("\n")


# Open a GitHub issue
def open_issue(
    title: str,
    body: str,
    repo_name: str,
    labels: tuple[str] = ("investigate", "changelog"),
):
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(repo_name)
    # Check if an issue with same title exists
    for issue in repo.get_issues():
        if issue.title == title:
            logger.info(f"Issue with title '{title}' already exists. Skipping...")
            return
    repo.create_issue(title=title, body=body, labels=list(labels))
    logger.info(f"Opened issue with title '{title}'")


async def main():
    try:
        html = await fetch_changelog()
    except Exception as e:
        logger.error(f"Error while fetching changelog: {e}")
        raise ConnectionError("Error while fetching changelog")

    try:
        entries = extract_entries(html)
    except Exception as e:
        logger.error(f"Error while extracting entries from changelog: {e}")
        raise ValueError("Error while extracting entries changelog")

    if not entries:
        raise RuntimeError(
            "No changelog entries found. The page structure may have changed."
        )

    logger.info(f"Found {len(entries)} entries in changelog")
    known_entries = read_known_entries()
    logger.info(f"Found {len(known_entries)} already known entries")

    new_entries_keys = set(entries) - set(known_entries)
    new_entries = {entry: entries[entry] for entry in new_entries_keys}

    if new_entries:
        if len(new_entries_keys) == 1:
            logger.info("Found 1 new entry. Opening issue for it...")
        else:
            logger.info(
                f"Found {len(new_entries_keys)} new entries. Opening issues for them..."
            )
        for entry in new_entries:
            title = f"New Notion API Changelog Entry: {new_entries[entry]['title']}"
            blog_post_url = f"{NOTION_CHANGELOG_URL}#{new_entries[entry]['section_id']}"
            body = f"**{entries[entry]['title']}**\n\n"
            # Pop the md content to avoid saving it on file
            entry_content_md = new_entries[entry].pop("content_md")
            for content in entry_content_md:
                body += f"{content}\n"
            body += "\n------------\n\n"
            body += f"Original blog post: [View here]({blog_post_url})\n"
            try:
                open_issue(title, body, GITHUB_REPOSITORY)
            except Exception as e:
                logger.error(f"Error while opening issue: {e}")
                raise ConnectionError("Error while opening issue")
        logger.info("Done!")

        # Save updated known entries
        logger.info("Saving updated known entries...")
        known_entries.update(new_entries)
        save_known_entries(known_entries)
        logger.info("Done!")


if __name__ == "__main__":
    asyncio.run(main())
