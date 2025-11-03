import json
import os

from notion_client import Client

try:
    from dotenv import load_dotenv

    load_dotenv()
except ModuleNotFoundError:
    pass

page_id = os.getenv("NOTION_PAGE_ID")
api_key = os.getenv("NOTION_API_KEY")

notion = Client(auth=api_key)

# ---------------------------------------------------------------------------

"""
Resources:
- Create a database endpoint (notion.databases.create(): https://developers.notion.com/reference/create-a-database)
- Working with databases guide: https://developers.notion.com/docs/working-with-databases
"""


def main():
    # Create a new database
    new_database = notion.databases.create(
        parent={
            "type": "page_id",
            "page_id": page_id,
        },
        title=[
            {
                "type": "text",
                "text": {
                    "content": "New database name",
                },
            },
        ],
        initial_data_source={
            "properties": {
                # These properties represent columns in the data source (i.e. its schema)
                "Grocery item": {
                    "type": "title",
                    "title": {},
                },
                "Price": {
                    "type": "number",
                    "number": {
                        "format": "dollar",
                    },
                },
                "Last ordered": {
                    "type": "date",
                    "date": {},
                },
            },
        },
    )

    # Print the new database response
    print(json.dumps(new_database, indent=2))


if __name__ == "__main__":
    main()
