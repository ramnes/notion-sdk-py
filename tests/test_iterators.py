import math
from random import random

from notion_client.helpers import EndpointIterator


# TODO return bad data / errors from endpoint
def mock_endpoint(item_count, page_size, **params):
    def page_generator(**kwargs):
        page_size = kwargs.get("page_size", 100)
        start = int(kwargs.get("start_cursor", 0))
        user_data = kwargs.get("user_data", None)
        pagenum = math.floor(start / page_size) + 1

        page = [
            {
                "index": x,
                "pagenum": pagenum,
                "content": user_data,
                "data": random(),
            }
            for x in range(start, start + page_size)
            if x < item_count
        ]

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

for item in iter:
    assert item["index"] == n_items
    assert item["pagenum"] == iter.page_number
    assert item["content"] == "testing"
    n_items += 1

assert n_items == 1042

################################################################################
# single full page

iter = EndpointIterator(endpoint=mock_endpoint(100, 100), user_data="one_page")

n_items = 0

for item in iter:
    assert item["content"] == "one_page"
    assert iter.last_page
    assert iter.page_number == 1
    n_items += 1

assert n_items == 100

################################################################################
# one result

iter = EndpointIterator(endpoint=mock_endpoint(1, 100))

n_items = 0

for item in iter:
    assert item["content"] is None
    assert iter.last_page
    assert iter.page_number == 1
    n_items += 1

assert n_items == 1

################################################################################
# empty result

iter = EndpointIterator(endpoint=mock_endpoint(0, 100))

n_items = 0

for item in iter:
    n_items += 1

assert n_items == 0
