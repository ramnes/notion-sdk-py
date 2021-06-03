import os
import sys

from notion_client.client import Client
from notion_client.helpers import EndpointIterator

api_key = (
    os.getenv("NOTION_API_KEY") or "secret_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
)
client = Client(auth=api_key)

page_id = sys.argv[1]

iter = EndpointIterator(endpoint=client.blocks.children.list, block_id=page_id)

n_items = 0

for item in iter:
    print(f'{item["type"]} => {item["id"]}')
    n_items += 1

print(f"total results: {n_items}")
