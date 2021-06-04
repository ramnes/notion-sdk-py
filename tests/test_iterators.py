import math
from random import random

from notion_client.helpers import EndpointIterator


def mock_endpoint(item_count, page_size, **params):
    def page_generator(**kwargs):
        page_size = kwargs.get("page_size", 100)
        start = int(kwargs.get("start_cursor", 0))
        user_data = kwargs.get("user_data", None)

        page = list()

        for x in range(start, start + page_size):
            if x < item_count:
                page.append(
                    {
                        "index": x,
                        "pagenum": math.ceil(x / page_size),
                        "content": user_data,
                        "data": random(),
                    }
                )

        return {
            "next_cursor": str(start + page_size),
            "has_more": (start + len(page) < item_count),
            "results": page,
        }

    return page_generator


################################################################################
# typical usage

iter = EndpointIterator(endpoint=mock_endpoint(1042, 100), user_data="testing")

n_items = 0
last_page = 0

for item in iter:
    assert item["index"] == n_items
    assert item["content"] == "testing"
    last_page = item["pagenum"]
    n_items += 1

assert n_items == 1042
assert last_page == 11

################################################################################
# empty result

iter = EndpointIterator(endpoint=mock_endpoint(0, 100))

n_items = 0

for item in iter:
    n_items += 1

assert n_items == 0
