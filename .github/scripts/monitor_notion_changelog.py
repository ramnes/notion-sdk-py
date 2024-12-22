import asyncio
import hashlib
import json
import logging
import os
from typing import Dict

from bs4 import BeautifulSoup
from github import Github
import httpx
from markdownify import markdownify as md

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

# Constants
NOTION_CHANGELOG_URL = "https://developers.notion.com/page/changelog"
DATA_FILE = ".github/scripts/known_entries.json"
GITHUB_REPOSITORY = "MassimoGennaro/notion-sdk-py"


async def fetch_changelog() -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(NOTION_CHANGELOG_URL)
        response.raise_for_status()
        return response.text


def extract_entries(html) -> Dict[str, Dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")

    # Extract all h2 headings with a specific class
    headings = soup.find_all("h2", class_="heading heading-2 header-scroll")
    parsed_data = {}

    for heading in headings:
        # Extract section id from the heading anchor
        section_id = (
            heading.find("div", class_="heading-anchor").get("id", None)
            if heading.find("div", class_="heading-anchor")
            else None
        )
        if section_id is None:
            continue

        # Extract date_text that will be used as title
        date_text = heading.text.strip()

        next_element = heading.find_next_sibling()
        content = ""  # It will be used as md5 and saved among known entries
        content_md = []  # It will be written ONLY on the issue
        while next_element and next_element.name not in {"h2"}:
            content += next_element.text.strip()
            content_md.append(md(repr(next_element)))
            next_element = next_element.find_next_sibling()

        # Update to dictionary,
        # keys are the md5 string of the content of each section
        md5_hash = hashlib.md5(content.encode()).hexdigest()
        parsed_data.update(
            {
                md5_hash: {
                    "section_id": section_id,
                    "title": date_text,
                    "content_md": content_md,
                }
            }
        )
    return parsed_data


def read_known_entries() -> Dict[str, Dict[str, str]]:
    if not os.path.exists(DATA_FILE):
        return dict()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_known_entries(entries: Dict[str, Dict[str, str]]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f)


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
                f"Found {len(new_entries_keys)} new entries. "
                f"Opening issues for them..."
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
                # pass
            except Exception as e:
                logger.error(f"Error while opening issue: {e}")
                raise ConnectionError("Error while opening issue")
        logger.info("Done!")

        # Save updated known entries
        logger.info("Saving updated known entries...")
        try:
            known_entries.update(new_entries)
            save_known_entries(known_entries)
        except Exception as e:
            logger.error(f"Error while saving updated known entries: {e}")
            logger.info("Deleting opened issues to maintain consistency...")
            try:
                for entry in new_entries:
                    title = (
                        f"New Notion API Changelog Entry: "
                        f"{new_entries[entry]['title']}"
                    )
                    g = Github(os.getenv("GITHUB_TOKEN"))
                    repo = g.get_repo(GITHUB_REPOSITORY)
                    for issue in repo.get_issues(labels=["changelog"], state="open"):
                        if issue.title == title:
                            issue.edit(state="closed")
                            break
            except Exception as e:
                logger.error(f"Error while deleting opened issues: {e}")
                raise ConnectionError("Error while deleting opened issues")
            logger.info("Done!")
            raise IOError("Error while saving updated known entries")
        logger.info("Done!")


if __name__ == "__main__":
    asyncio.run(main())
