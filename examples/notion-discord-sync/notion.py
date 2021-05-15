import os
from notion_client import Client
from pprint import pprint
import json

def add_recommendation(rec):
    db_id = os.getenv('DATABASE_ID')
    notion = Client(auth=os.getenv('NOTION_TOKEN'))
    book_file = open("mock_book_details.json")
    genres = ["Fiction", "Futuristic"]
    book = json.load(book_file)
    print(book)
    response = notion.pages.create(
        **book
    )
    response = notion.databases.retrieve(
        **{
            "database_id": "526652e3-0e53-4606-a263-a07702d4482c"
        }
    )
    print(json.dumps(response.json()))
