import json
import logging
import os
from typing import Dict

from bs4 import BeautifulSoup
from github import Github
import httpx

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


def html_to_markdown(element) -> str:
    """
    Convert an HTML element to Markdown text.
    """
    match element.name:
        case "p":
            return element.text.strip()
        case "strong" | "b":
            return f"**{element.text.strip()}**"
        case "em" | "i":
            return f"*{element.text.strip()}*"
        case "ul":
            items = [f"- {li.text.strip()}" for li in element.find_all("li")]
            return "\n".join(items)
        case "ol":
            items = [
                f"{i + 1}. {li.text.strip()}"
                for i, li in enumerate(element.find_all("li"))
            ]
            return "\n".join(items)
        case "h1" | "h2" | "h3" | "h4" | "h5" | "h6":
            level = int(element.name[1])
            return f"{'#' * level} {element.text.strip()}"
        case "a":
            href = element.get("href", "#")
            return f"[{element.text.strip()}]({href})"
        case _:
            return element.text.strip()


def extract_entries(html) -> Dict[str, Dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    # Extract all h2 headings with a specific class
    headings = soup.find_all("h2", class_="heading heading-2 header-scroll")
    logger.info(f"Found {len(headings)} entries in changelog")

    parsed_data = {}

    for heading in headings:
        # Extract the date from the text or the id attribute
        section_id = (
            heading.find("div", class_="heading-anchor").get("id", None)
            if heading.find("div", class_="heading-anchor")
            else None
        )
        if section_id is None:
            continue
        date_text = heading.text.strip()  # Extract the visible text

        next_element = heading.find_next_sibling()
        content = []
        while next_element and next_element.name not in {"h2"}:
            markdown_text = html_to_markdown(next_element)
            if markdown_text:
                content.append(markdown_text)
            next_element = next_element.find_next_sibling()

        # Append the parsed data as a dictionary
        parsed_data.update({section_id: {"date_text": date_text, "content": content}})
    return parsed_data


def read_known_entries() -> Dict[str, Dict[str, str]]:
    if not os.path.exists(DATA_FILE):
        return dict()
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_known_entries(entries: Dict[str, Dict[str, str]]):
    with open(DATA_FILE, "w") as f:
        json.dump(entries, f)


# Open a GitHub issue
def open_issue(title: str, body: str, repo_name: str):
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(repo_name)
    # Check if an issue with same title exists
    for issue in repo.get_issues():
        if issue.title == title:
            logger.info(f"Issue with title '{title}' already exists. Skipping...")
            return
    repo.create_issue(title=title, body=body)
    logger.info(f"Opened issue with title '{title}'")


async def main():
    html = await fetch_changelog()
    entries = extract_entries(html)
    logger.info(f"Found {len(entries)} entries in changelog")
    known_entries = read_known_entries()
    logger.info(f"Found {len(known_entries)} already known entries")

    new_entries_keys = [entry for entry in entries if entry not in known_entries]

    if new_entries_keys:
        if len(new_entries_keys) == 1:
            logger.info("Found 1 new entry. Opening issue for it...")
        else:
            logger.info(
                f"Found {len(new_entries_keys)} new entries. "
                f"Opening issue for them..."
            )
        for entry in new_entries_keys:
            title = f"New Notion API Changelog Entry: {entries[entry]['date_text']}"
            body = f"**{entries[entry]['date_text']}**\n\n"
            for content in entries[entry]["content"]:
                body += f"{content}\n"
            open_issue(title, body, GITHUB_REPOSITORY)
        logger.info("Done!")

        # Save updated known entries
        logger.info("Saving updated known entries...")
        save_known_entries(entries)
        logger.info("Done!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
