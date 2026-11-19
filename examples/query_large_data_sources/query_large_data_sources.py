import os
import time

from notion_client import Client
from notion_client.helpers import (
    collect_paginated_api,
    is_full_page_or_data_source,
    iterate_paginated_api,
)

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    pass
else:
    load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_DATA_SOURCE_ID = os.getenv("NOTION_DATA_SOURCE_ID", "")

while NOTION_API_KEY == "":
    NOTION_API_KEY = input("Enter your Notion integration token: ").strip()

while NOTION_DATA_SOURCE_ID == "":
    NOTION_DATA_SOURCE_ID = input("Enter the Notion data source ID: ").strip()

# NOTION_BASE_URL and NOTION_VERSION are optional overrides for non-default
# hosts. Leave them unset to use api.notion.com and the SDK's default version.
client_options = {}
if os.getenv("NOTION_BASE_URL"):
    client_options["base_url"] = os.environ["NOTION_BASE_URL"]
if os.getenv("NOTION_VERSION"):
    client_options["notion_version"] = os.environ["NOTION_VERSION"]

notion = Client(auth=NOTION_API_KEY, **client_options)

# A single query (one filter + sort) returns at most a fixed number of rows:
# 10,000 by default. When that limit is reached, has_more becomes False and the
# response carries request_status["type"] == "incomplete". The SDK pagination
# helpers follow next_cursor until has_more is False, so on a data source larger
# than the limit they stop at 10,000 and silently return a partial set.
#
# query_all_rows below works around the limit. See the README for the why.


def stream_first_rows(data_source_id, limit):
    """Print the IDs of the first `limit` rows, one row at a time.

    The simple way, for data sources under the limit. iterate_paginated_api
    streams the rows so you never hold the whole data source in memory.
    """
    shown = 0
    for row in iterate_paginated_api(
        notion.data_sources.query,
        data_source_id=data_source_id,
        page_size=min(limit, 100),
    ):
        print(f"  {row['id']}")
        shown += 1
        if shown >= limit:
            break


def collect_all(data_source_id):
    """Gather every row into a list.

    Also the simple way: only use it when you know the result fits in memory
    and stays under the limit.
    """
    return collect_paginated_api(
        notion.data_sources.query, data_source_id=data_source_id
    )


def query_all_rows(data_source_id):
    """Get every row, even when the data source exceeds the per-query limit.

    The trick: the limit is per query, where a query is identified by its filter
    and sort. Change the filter and you get a fresh query with its own budget.
    So we walk the data source in created_time windows. Sort by created_time
    ascending; each time a window hits the limit, start a new query filtered to
    created_time on_or_after the last row we saw. Rows on a window boundary
    share that timestamp and repeat across windows, so we de-duplicate by id.

    created_time is used because it never changes. last_edited_time would move
    rows between windows as they are edited, which would drop or double-count
    rows.
    """
    rows_by_id = {}
    window_start = None

    while True:
        limit_reached = False
        last_created_time = None
        cursor = None

        # Drain one window: page through it until next_cursor is empty. This
        # loop also ends when the per-query limit is hit, because the limit sets
        # has_more to False (and request_status to incomplete).
        while True:
            query = {
                "data_source_id": data_source_id,
                "sorts": [{"timestamp": "created_time", "direction": "ascending"}],
                "start_cursor": cursor,
                "page_size": 100,
            }
            if window_start:
                query["filter"] = {
                    "timestamp": "created_time",
                    "created_time": {"on_or_after": window_start},
                }
            response = notion.data_sources.query(**query)

            for row in response["results"]:
                rows_by_id[row["id"]] = row
                # Pages and child data sources (wikis) both carry created_time,
                # and either can be the window's last row, so advance on either.
                if is_full_page_or_data_source(row):
                    last_created_time = row["created_time"]

            request_status = response.get("request_status") or {}
            if request_status.get("type") == "incomplete":
                limit_reached = True
            cursor = response.get("next_cursor")
            if not cursor:
                break

        # The window finished under the limit: we have everything.
        if not limit_reached:
            break
        # The window hit the limit but every row shares one created_time, so we
        # cannot advance by time. Narrow the query with another filter instead.
        if not last_created_time or last_created_time == window_start:
            raise RuntimeError(
                "More than the per-query limit share created_time "
                f"{last_created_time}. Add another filter to split this window."
            )

        window_start = last_created_time
        print(f"  hit the limit; continuing from created_time {window_start}")

    return list(rows_by_id.values())


def main():
    print(f"Data source: {NOTION_DATA_SOURCE_ID}\n")

    print("First few rows (streamed with iterate_paginated_api):")
    stream_first_rows(NOTION_DATA_SOURCE_ID, 5)

    print("\nFetching every row (created_time windowing):")
    started = time.monotonic()
    all_rows = query_all_rows(NOTION_DATA_SOURCE_ID)
    print(f"\nGot {len(all_rows)} rows in {time.monotonic() - started:.1f}s")

    # collect_all (above) is the one-liner you reach for when the data source
    # is small enough to fit in memory and under the limit. Uncomment to
    # compare; on a large data source it stops at the per-query limit.
    # capped = collect_all(NOTION_DATA_SOURCE_ID)
    # print(f"collect_paginated_api returned {len(capped)} rows")


if __name__ == "__main__":
    main()
