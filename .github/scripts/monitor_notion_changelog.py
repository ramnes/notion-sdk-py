import json
import logging
import os
from typing import Dict

from bs4 import BeautifulSoup
import httpx

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

# Constants
NOTION_CHANGELOG_URL = "https://developers.notion.com/page/changelog"
DATA_FILE = ".github/scripts/known_entries.json"


async def fetch_changelog() -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(NOTION_CHANGELOG_URL)
        response.raise_for_status()
        return response.text


def extract_entries(html) -> Dict[str, Dict[str, str]]:
    known_entries = read_known_entries()
    logger.info(f"Found {len(known_entries)} known entries")
    soup = BeautifulSoup(html, "html.parser")
    # Extract all h2 headings with a specific class
    headings = soup.find_all("h2", class_="heading heading-2 header-scroll")
    logger.info(f"Found {len(headings)} entries in changelog")

    parsed_data = known_entries.copy()

    for heading in headings:
        # Extract the date from the text or the id attribute
        section_id = (
            heading.find("div", class_="heading-anchor").get("id", None)
            if heading.find("div", class_="heading-anchor")
            else None
        )
        if section_id is None:
            continue
        if section_id in known_entries:
            continue
        date_text = heading.text.strip()  # Extract the visible text

        # Extract all inner `li` content for the current section
        ul = heading.find_next_sibling("ul")  # Find the first `ul` after this h2
        content = []
        if ul:
            for item in ul.find_all("li"):
                content.append(item.text.strip())

        # Append the parsed data as a dictionary
        parsed_data.update({section_id: {"date_text": date_text, "content": content}})
    logger.info(f"Parsed {len(parsed_data) - len(known_entries)} new entries")
    return parsed_data


def read_known_entries() -> Dict[str, Dict[str, str]]:
    if not os.path.exists(DATA_FILE):
        return dict()
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_known_entries(entries: Dict[str, Dict[str, str]]):
    with open(DATA_FILE, "w") as f:
        json.dump(entries, f)


async def main():
    html = await fetch_changelog()
    entries = extract_entries(html)
    save_known_entries(entries)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
