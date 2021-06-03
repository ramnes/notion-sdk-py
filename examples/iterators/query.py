import os
import sys

from notion_client.client import Client
from notion_client.helpers import QueryIterator

api_key = (
    os.getenv("NOTION_API_KEY") or "secret_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
)
client = Client(auth=api_key)

dbid = sys.argv[1]

iter = QueryIterator(
    client=client,
    database_id=dbid,
    sorts=[{"direction": "ascending", "timestamp": "last_edited_time"}],
)

n_items = 0

for item in iter:
    print(f'{item["id"]} => {item["properties"]["Name"]}')
    n_items += 1

print(f"total results: {n_items}")
