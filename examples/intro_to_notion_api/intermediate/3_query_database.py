import json
import os

from notion_client import Client

from sample_data import properties_for_new_pages

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
- Create a page endpoint (notion.pages.create(): https://developers.notion.com/reference/post-page)
- Working with databases guide: https://developers.notion.com/docs/working-with-databases
Query a database: https://developers.notion.com/reference/post-database-query
Filter database entries: https://developers.notion.com/reference/post-database-query-filter
"""


def add_notion_page_to_data_source(data_source_id, page_properties):
    notion.pages.create(
        parent={
            "data_source_id": data_source_id,
        },
        properties=page_properties,  # Note: Page properties must match the schema of the database
    )


def query_data_source(data_source_id):
    print("Querying database...")
    # This query will filter database entries and return pages that have a "Last ordered"
    # property that is more recent than 2022-12-31. Use multiple filters with the AND/OR
    # options: https://developers.notion.com/reference/post-database-query-filter.
    last_ordered_in_2023 = notion.data_sources.query(
        data_source_id=data_source_id,
        filter={
            "property": "Last ordered",
            "date": {
                "after": "2022-12-31",
            },
        },
    )

    # Print filtered results
    print('Pages with the "Last ordered" date after 2022-12-31:')
    print(json.dumps(last_ordered_in_2023, indent=2))


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
                    "content": "Grocery list",
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

    if new_database["object"] != "database":
        print(f"No read permissions on database: {new_database['id']}")
        return

    # Print the new database's URL. Visit the URL in your browser to see the pages that get created in the next step.
    print(new_database["id"])

    data_source_id = new_database["data_sources"][0]["id"]
    if not data_source_id:  # If there is no ID (if there's an error), return.
        return

    print("Adding new pages...")
    for i in range(len(properties_for_new_pages)):
        # Add a few new pages to the database that was just created
        add_notion_page_to_data_source(data_source_id, properties_for_new_pages[i])

    # After adding pages, query the database entries (pages)
    query_data_source(data_source_id)


if __name__ == "__main__":
    main()
