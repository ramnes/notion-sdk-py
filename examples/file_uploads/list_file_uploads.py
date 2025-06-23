import os
import sys

from notion_client import Client
from notion_client.helpers import get_id


from notion_client.notion_mime_detector import NotionMIMETypeDetector
# import httpx


import json
from typing import Dict

from dotenv import load_dotenv

if os.getenv("ENV") != "production":
    load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")

while NOTION_TOKEN == "":
    print("NOTION_TOKEN not found.")
    NOTION_TOKEN = input("Enter your integration token: ").strip()

# Initialize the client
notion = Client(auth=NOTION_TOKEN)

def main():

    response = notion.file_uploads.list()
    print(type(response))
    print("List of file uploads:")
    # print(response)
    data: Dict = response
    with open("./file_uploads.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



if __name__ == "__main__":
    main()

