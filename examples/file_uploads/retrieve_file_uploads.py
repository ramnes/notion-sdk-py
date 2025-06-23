import os
import sys

from notion_client import Client
from notion_client.helpers import get_id

from notion_client.notion_mime_detector import NotionMIMETypeDetector




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
    file_upload_id = "21a99f72-bada-81a9-9dd9-00b28cf7508b"
    response = notion.file_uploads.retrieve(file_upload_id = file_upload_id)
    print(type(response))
    print("Retrieved file upload:")
    print(response)



if __name__ == "__main__":
    main()
