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
pprint(result.get("properties", {}))

# Resolve a data source ID compatible with 2025-09-03
data_source_id = None
if result.get("object") == "data_source":
    data_source_id = result["id"]
elif result.get("object") == "database":
    # Retrieve the database to get its data_sources list
    db = notion.databases.retrieve(result["id"])
    if db.get("data_sources"):
        data_source_id = db["data_sources"][0]["id"]
if not data_source_id:
    raise RuntimeError("Could not resolve a data source from search results.")

# Create a new page
your_name = input("\n\nEnter your name: ")
gh_uname = input("Enter your github username: ")
new_page = {
    "Name": {"title": [{"text": {"content": your_name}}]},
    "Tags": {"type": "multi_select", "multi_select": [{"name": "python"}]},
    # Properties like this must exist in the database columns
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

content = [
    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": (
                            "The content of your page goes here. See https://developers.notion.com/reference/post-page"
                        )
                    },
                }
            ]
        },
    }
]
notion.pages.create(
    parent={"type": "data_source_id", "data_source_id": data_source_id},
    properties=new_page,
    children=content,
)
print("You were added to the People database!")


# Query a database
name = input("\n\nEnter the name of the person to search in People: ")
results = notion.data_sources.query(
    data_source_id=data_source_id,
    filter={"property": "Name", "rich_text": {"contains": name}},
).get("results")

no_of_results = len(results)

if no_of_results == 0:
    print("No results found.")
    sys.exit()

print(f"No of results found: {len(results)}")

result = results[0]

print(f"The first result is a {result['object']} with id {result['id']}.")
print(f"This was created on {result['created_time']}")
