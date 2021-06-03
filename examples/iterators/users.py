import os

from notion_client.client import Client
from notion_client.helpers import EndpointIterator

api_key = (
    os.getenv("NOTION_API_KEY") or "secret_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
)
client = Client(auth=api_key)

iter = EndpointIterator(client.users.list)

n_items = 0

for item in iter:
    print(f'{item["name"]} [{item["type"]}] => {item["id"]}')
    n_items += 1

print(f"total results: {n_items}")
