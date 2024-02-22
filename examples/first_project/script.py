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
print("\nSearching for the word 'People' ")
results = notion.search(query="People").get("results")
print(len(results))
result = results[0]
print("The result is a", result["object"])
pprint(result["properties"])

database_id = result["id"]  # store the database id in a variable for future use

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
        "filter": {"property": "Name", "rich_text": {"contains": name}},
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
