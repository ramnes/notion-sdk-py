<!-- markdownlint-disable -->
![notion-sdk-py](https://socialify.git.ci/ramnes/notion-sdk-py/image?font=Bitter&language=1&logo=https%3A%2F%2Fupload.wikimedia.org%2Fwikipedia%2Fcommons%2F4%2F45%2FNotion_app_logo.png&owner=1&pattern=Circuit%20Board&theme=Light)

<div align="center">
  <p>
    <a href="https://pypi.org/project/notion-client"><img src="https://img.shields.io/pypi/v/notion-client.svg" alt="PyPI"></a>
    <a href="tox.ini"><img src="https://img.shields.io/pypi/pyversions/notion-client" alt="Supported Python Versions"></a>
    <br/>
    <a href="LICENSE"><img src="https://img.shields.io/github/license/ramnes/notion-sdk-py" alt="License"></a>
    <a href="https://github.com/ambv/black"><img src="https://img.shields.io/badge/code%20style-black-black" alt="Code style"></a>
    <a href="https://codecov.io/github/ramnes/notion-sdk-py"><img src="https://codecov.io/gh/ramnes/notion-sdk-py/branch/main/graphs/badge.svg" alt="Coverage"></a>
    <a href="https://pypistats.org/packages/notion-client"><img src="https://img.shields.io/pypi/dm/notion-client" alt="Package downloads"></a>
    <br/>
    <a href="https://github.com/ramnes/notion-sdk-py/actions/workflows/quality.yml"><img src="https://github.com/ramnes/notion-sdk-py/actions/workflows/quality.yml/badge.svg" alt="Code Quality"></a>
    <a href="https://github.com/ramnes/notion-sdk-py/actions/workflows/test.yml"><img src="https://github.com/ramnes/notion-sdk-py/actions/workflows/test.yml/badge.svg" alt="Tests"></a>
    <a href="https://github.com/ramnes/notion-sdk-py/actions/workflows/docs.yml"><img src="https://github.com/ramnes/notion-sdk-py/actions/workflows/docs.yml/badge.svg" alt="Docs"></a>
  </p>
</div>
<!-- markdownlint-enable -->

**_notion-sdk-py_ is a simple and easy to use client library for the official
[Notion API](https://developers.notion.com/).**

It is meant to be a Python version of the reference [JavaScript SDK](https://github.com/makenotion/notion-sdk-js),
so usage should be very similar between both. 😊 (If not, please open an issue
or PR!)

<!-- markdownlint-disable -->
## Installation
<!-- markdownlint-enable -->
```shell
pip install notion-client
```

## Usage

> Use Notion's [Getting Started Guide](https://developers.notion.com/docs/getting-started)
> to get set up to use Notion's API.

Import and initialize a client using an **integration token** or an
OAuth **access token**.

```python
import os
from notion_client import Client

notion = Client(auth=os.environ["NOTION_TOKEN"])
```

In an asyncio environment, use the asynchronous client instead:

```python
from notion_client import AsyncClient

notion = AsyncClient(auth=os.environ["NOTION_TOKEN"])
```

Make a request to any Notion API endpoint.

```python
from pprint import pprint

list_users_response = notion.users.list()
pprint(list_users_response)
```

> [!NOTE]
> See the complete list of endpoints in the [API reference](https://developers.notion.com/reference).

or with the asynchronous client:

```python
list_users_response = await notion.users.list()
pprint(list_users_response)
```

This would output something like:

```text
{'results': [{'avatar_url': 'https://secure.notion-static.com/e6a352a8-8381-44d0-a1dc-9ed80e62b53d.jpg',
              'id': 'd40e767c-d7af-4b18-a86d-55c61f1e39a4',
              'name': 'Avocado Lovelace',
              'object': 'user',
              'person': {'email': 'avo@example.org'},
              'type': 'person'},
             ...]}
```

All API endpoints are available in both the synchronous and asynchronous clients.

Endpoint parameters are grouped into a single object. You don't need to remember
which parameters go in the path, query, or body.

```python
my_page = notion.data_sources.query(
    **{
        "data_source_id": "897e5a76-ae52-4b48-9fdf-e71f5945d1af",
        "filter": {
            "property": "Landmark",
            "rich_text": {
                "contains": "Bridge",
            },
        },
    }
)
```

### Handling errors

If the API returns an unsuccessful response, an `APIResponseError` will be raised.

The error contains properties from the response, and the most helpful is `code`.
You can compare `code` to the values in the `APIErrorCode` object to avoid
misspelling error codes.

```python
import logging
from notion_client import APIErrorCode, APIResponseError, Client

try:
    notion = Client(auth=os.environ["NOTION_TOKEN"])
    my_page = notion.data_sources.query(
        **{
            "data_source_id": "897e5a76-ae52-4b48-9fdf-e71f5945d1af",
            "filter": {
                "property": "Landmark",
                "rich_text": {
                    "contains": "Bridge",
                },
            },
        }
    )
except APIResponseError as error:
    if error.code == APIErrorCode.ObjectNotFound:
        #
        # For example: handle by asking the user to select a different data source
        #
        ...
    else:
        # Other error handling code
        print(error)
```

### Logging

The client emits useful information to a logger. By default, it only emits warnings
and errors.

If you're debugging an application, and would like the client to log request & response
bodies, set the `log_level` option to `logging.DEBUG`.

```python
import logging
from notion_client import Client

notion = Client(
    auth=os.environ["NOTION_TOKEN"],
    log_level=logging.DEBUG,
)
```

You may also set a custom `logger` to emit logs to a destination other than `stdout`.
Have a look at [Python's logging cookbook](https://docs.python.org/3/howto/logging-cookbook.html)
if you want to create your own logger.

### Client options

`Client` and `AsyncClient` both support the following options on initialization.
These options are all keys in the single constructor parameter.

<!-- markdownlint-disable -->
| Option       | Default value              | Type              | Description                                                                                             |
| ------------ | -------------------------- | ----------------- | ------------------------------------------------------------------------------------------------------- |
| `auth`       | `None`                     | `string`          | Bearer token for authentication. If left undefined, the `auth` parameter should be set on each request. |
| `log_level`  | `logging.WARNING`          | `int`             | Verbosity of logs the instance will produce. By default, logs are written to `stdout`.                  |
| `timeout_ms` | `60_000`                   | `int`             | Number of milliseconds to wait before emitting a `RequestTimeoutError`                                  |
| `base_url`   | `"https://api.notion.com"` | `string`          | The root URL for sending API requests. This can be changed to test with a mock server.                  |
| `logger`     | Log to console             | `logging.Logger`  | A custom logger.                                                                                        |
<!-- markdownlint-enable -->

### Full API responses

The following functions can distinguish between full and partial API responses.

<!-- markdownlint-disable -->
| Function                      | Purpose                                                                                                                                                                        |
| --------------------------    | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `is_full_page`                | Determine whether an object is a full [Page object](https://developers.notion.com/reference/page)                                                                              |
| `is_full_block`               | Determine whether an object is a full [Block object](https://developers.notion.com/reference/block)                                                                            |
| `is_full_data_source`         | Determine whether an object is a full [Data source object](https://developers.notion.com/reference/data-source)                                                                |
| `is_full_page_or_data_source` | Determine whether an object is a full [Page object](https://developers.notion.com/reference/page) or [Data source object](https://developers.notion.com/reference/data-source) |
| `is_full_user`                | Determine whether an object is a full [User object](https://developers.notion.com/reference/user)                                                                              |
| `is_full_comment`             | Determine whether an object is a full [Comment object](https://developers.notion.com/reference/comment-object)                                                                 |
<!-- markdownlint-enable -->

```python
from notion_client.helpers import is_full_page

full_or_partial_pages = notion.data_sources.query(
    data_source_id="897e5a76-ae52-4b48-9fdf-e71f5945d1af"
)

for page in full_or_partial_pages["results"]:
    if not is_full_page_or_data_source(page):
        continue
    print(f"Created at: {page['created_time']}")
```

### Utility functions

This package also exports a few utility functions that are helpful for dealing
with any of the paginated APIs.

#### `iterate_paginated_api(function, **kwargs)`

This utility turns any paginated API into a generator.

**Parameters:**

- `function`: Any function on the Notion client that represents a paginated API
  (i.e. accepts `start_cursor`.) Example: `notion.blocks.children.list`.
- `**kwargs`: Arguments that should be passed to the API on the first and
  subsequent calls to the API, for example a `block_id`.

**Returns:**

A generator over results from the API.

**Example:**

```python
from notion_client.helpers import iterate_paginated_api

for block in iterate_paginated_api(
    notion.blocks.children.list, block_id=parent_block_id
):
    # Do something with block.
    ...
```

#### `collect_paginated_api(function, **kwargs)`

This utility accepts the same arguments as `iterate_paginated_api`, but collects
the results into an in-memory array.

Before using this utility, check that the data you are dealing with is small
enough to fit in memory.

**Parameters:**

- `function`: Any function on the Notion client that represents a paginated API
  (i.e. accepts `start_cursor`.) Example: `notion.blocks.children.list`.
- `**kwargs`: Arguments that should be passed to the API on the first and
  subsequent calls to the API, for example a `block_id`.

**Returns:**

An array with results from the API.

**Example:**

```python
from notion_client.helpers import collect_paginated_api

blocks = collect_paginated_api(
    notion.blocks.children.list, block_id=parent_block_id
)
# Do something with blocks.
```

Both utilities also have async versions: `async_iterate_paginated_api` and
`async_collect_paginated_api`.

### Custom requests

To make requests directly to a Notion API endpoint instead of using the
pre-built families of methods, call the `request()` method. For example:

```python
import json

# POST /v1/comments
response = notion.request(
    path="comments",
    method="post",
    body={
        "parent": {"page_id": "5c6a28216bb14a7eb6e1c50111515c3d"},
        "rich_text": [{"text": {"content": "Hello, world!"}}],
    },
    # No `query` params in this example, only `body`.
)

print(json.dumps(response, indent=2))
```

> [!TIP]
> Usually, making custom requests with `notion.request()` isn't necessary, but
> can be helpful in some cases, e.g. when upgrading your [Notion API version](https://developers.notion.com/reference/versioning)
> incrementally before upgrading your SDK version. For example, if there's a new
> or renamed endpoint in the new API version that isn't yet available to call
> via a dedicated method on `Client`.
>
> In the above example, the simpler approach is to use
> `notion.comments.create()`.

Another customization you can make is to pass your own `httpx.Client` or
`httpx.AsyncClient` to the `Client` or `AsyncClient` constructor. This might be
helpful for some execution environments where the default HTTPX client isn't
suitable.

## Testing

Run the tests with the `pytest` command. If you want to test against all Python
versions, you can run `tox` instead.

The tests are using `pytest-vcr`'s cassettes for simulating requests to the
Notion API. To create new tests or run them without cassettes, you need to set
up the environment variables `NOTION_TOKEN` and `NOTION_TEST_PAGE_ID` (a page
where your integration has all the capabilities enabled).

The code will use the page at `NOTION_TEST_PAGE_ID` to generate a temporary
environment with the Notion objects to be tested, which will be deleted
at the end of the session.

## Requirements and compatibility

This package supports the following minimum versions:

- Runtime: Python >= 3.8
- httpx >= 0.23.0

Earlier versions may still work, but we encourage people building new applications
to upgrade to the current stable.

## Getting help

If you want to submit a feature request for Notion's API, or are experiencing
any issues with the API platform, please email `developers@makenotion.com`.

If you found a bug with the library, please [submit an issue](https://github.com/ramnes/notion-sdk-py/issues).
