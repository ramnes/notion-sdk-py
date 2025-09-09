import os

from notion_client import Client


def main() -> None:
    token = os.getenv("NOTION_TOKEN", "")
    if not token:
        token = input("Enter your NOTION_TOKEN: ").strip()
    client = Client(auth=token)

    # Database to attach the new data source to
    database_id = os.getenv("NOTION_DATABASE_ID", "")
    if not database_id:
        database_id = input("Enter target database_id: ").strip()

    # Minimal schema for the new data source
    properties = {
        "Name": {"title": {}},
        "Status": {"select": {"options": [{"name": "Todo"}, {"name": "Done"}]}},
    }

    print("Creating data source under database:", database_id)
    ds = client.data_sources.create(
        parent={"type": "database_id", "database_id": database_id},
        properties=properties,
        title=[{"text": {"content": "API-created Data Source"}}],
    )
    print("Created data source:", ds.get("id"))


if __name__ == "__main__":
    main()
