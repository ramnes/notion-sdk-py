import os
import sys
from pprint import pprint

from notion_client import Client

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    print("Could not load .env because python-dotenv not found.")
else:
    load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")

while NOTION_TOKEN == "":
    print("NOTION_TOKEN not found.")
    NOTION_TOKEN = input("Enter your integration token: ").strip()

# Initialize the client
notion = Client(auth=NOTION_TOKEN)


# Search for an item
print(
    "\nSearching for the word 'PeopleNotionSdkTest' "
)  # Change the name of the example database to something very specific
results = notion.search(query="PeopleNotionSdkTest").get("results")
print(len(results))
result = results[0]
print("The result is a", result["object"])
pprint(result["properties"])

database_id = result["id"]  # store the database id in a variable for future use
parent_page_id = result["parent"]["page_id"]

print(f"The database is in page {parent_page_id} ")

# Create a new page
your_name = input("\n\nEnter your name: ")
gh_uname = input("Enter your github username: ")
new_page = {
    "Name": {"title": [{"text": {"content": your_name}}]},
    "Tags": {"type": "multi_select", "multi_select": [{"name": "python"}]},
    "GitHub": {
        "type": "rich_text",
        "rich_text": [
            {
                "type": "text",
                "text": {"content": gh_uname},
            },
        ],
    },
}
notion.pages.create(parent={"database_id": database_id}, properties=new_page)
print("You were added to the People database!")


# Query a database
name = input("\n\nEnter the name of the person to search in People: ")
results = notion.databases.query(
    **{
        "database_id": database_id,
        "filter": {"property": "Name", "text": {"contains": name}},
    }
).get("results")

no_of_results = len(results)

if no_of_results == 0:
    print("No results found.")
    sys.exit()

print(f"No of results found: {len(results)}")

result = results[0]

print(f"The first result is a {result['object']} with id {result['id']}.")
print(f"This was created on {result['created_time']}")


# Create a database

properties = {
    "Name": {"title": {}},
    "Description": {"rich_text": {}},
    "In stock": {"checkbox": {}},
    "Food group": {
        "select": {
            "options": [
                {"name": "🥦 Vegetable", "color": "green"},
                {"name": "🍎 Fruit", "color": "red"},
                {"name": "💪 Protein", "color": "yellow"},
            ]
        }
    },
    "Price": {"number": {"format": "dollar"}},
    "Last ordered": {"date": {}},
    "Store availability": {
        "type": "multi_select",
        "multi_select": {
            "options": [
                {"name": "Duc Loi Market", "color": "blue"},
                {"name": "Rainbow Grocery", "color": "gray"},
                {"name": "Nijiya Market", "color": "purple"},
                {"name": "Gus's Community Market", "color": "yellow"},
            ]
        },
    },
    "+1": {"people": {}},
    "Photo": {"files": {}},
}
title = [{"type": "text", "text": {"content": "Grocery List"}}]
icon = {"type": "emoji", "emoji": "🎉"}
parent = {"type": "page_id", "page_id": parent_page_id}
newdb = notion.databases.create(
    parent=parent, title=title, properties=properties, icon=icon
)

print(f"Database {newdb['id']} has been created.")
