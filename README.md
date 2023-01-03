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
    <a href="https://snyk.io/advisor/python/notion-client"><img src="https://snyk.io/advisor/python/notion-client/badge.svg" alt="Package health"></a>
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
so usage should be pretty similar between both. 😊

> 📢 **Announcement** (10-12-2022) — Release 2.0.0 is out! It mostly adds new
> helpers, support for the comments API, more tests, and Python 3.11.
>
> Beware, `Notion-Version` has been upgraded to `2022-06-28` and it brings
> [breaking changes](https://developers.notion.com/changelog/releasing-notion-version-2022-06-28).

<!-- markdownlint-disable -->
## Installation
<!-- markdownlint-enable -->
```shell
pip install notion-client
```

## Usage

> Before getting started, [create an integration](https://www.notion.com/my-integrations)
> and find the token.
> [→ Learn more about authorization](https://developers.notion.com/docs/authorization).

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

> See the complete list of endpoints in the [API reference](https://developers.notion.com/reference).

```python
from pprint import pprint

list_users_response = notion.users.list()
pprint(list_users_response)
```

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
my_page = notion.databases.query(
    **{
        "database_id": "897e5a76-ae52-4b48-9fdf-e71f5945d1af",
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
from notion_client import APIErrorCode, APIResponseError

try:
    my_page = notion.databases.query(
        **{
            "database_id": "897e5a76-ae52-4b48-9fdf-e71f5945d1af",
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
        ...  # For example: handle by asking the user to select a different database
    else:
        # Other error handling code
        logging.error(error)
```

### Logging

The client emits useful information to a logger. By default, it only emits warnings
and errors.

If you're debugging an application, and would like the client to log request & response
bodies, set the `log_level` option to `logging.DEBUG`.

```python
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
| Option | Default value | Type | Description |
|--------|---------------|---------|-------------|
| `auth` | `None` | `string` | Bearer token for authentication. If left undefined, the `auth` parameter should be set on each request. |
| `log_level` | `logging.WARNING` | `int` | Verbosity of logs the instance will produce. By default, logs are written to `stdout`.
| `timeout_ms` | `60_000` | `int` | Number of milliseconds to wait before emitting a `RequestTimeoutError` |
| `base_url` | `"https://api.notion.com"` | `string` | The root URL for sending API requests. This can be changed to test with a mock server. |
| `logger` | Log to console | `logging.Logger` | A custom logger. |

### Full API responses

The following functions can distinguish between full and partial API responses.

| Function | Purpose                                                        |
| ------------------- | -------------------------------------------------------------- |
| `is_full_page`        | Determine whether an object is a full [Page object](https://developers.notion.com/reference/page)   |
| `is_full_block`       | Determine whether an object is a full [Block object](https://developers.notion.com/reference/block)  |
| `is_full_database`    | Determine whether an object is a full [Database object](https://developers.notion.com/reference/database)  |
| `is_full_user`        | Determine whether an object is a full [User object](https://developers.notion.com/reference/user)  |
| `is_full_comment`     | Determine whether an object is a full [Comment object](https://developers.notion.com/reference/comment-object)  |
<!-- markdownlint-enable -->

```python
from notion_client.helpers import is_full_page

full_or_partial_pages = await notion.databases.query(
    database_id="897e5a76-ae52-4b48-9fdf-e71f5945d1af"
)

for page in full_or_partial_pages["results"]:
    if not is_full_page(page):
        continue
    print(f"Created at: {page['created_time']}")
```

### Utility functions

These functions can be helpful for dealing with any of the paginated APIs.

`iterate_paginated_api(function, **kwargs)` and its async version
`async_iterate_paginated_api(function, **kwargs)` turn any paginated API into a generator.

The `function` parameter must accept a `start_cursor` argument. Example: `notion.blocks.children.list`.

```python
from notion_client.helpers import iterate_paginated_api

for block in iterate_paginated_api(
    notion.databases.query, database_id="897e5a76-ae52-4b48-9fdf-e71f5945d1af"
):
    # Do something with block.
    ...
```

If you don't need a generator, `collect_paginated_api(function, **kwargs)` and
its async version `async_collect_paginated_api(function, **kwargs)` have the
same behavior than the previous functions, but return a list of all results
from the paginated API.

```python
from notion_client.helpers import collect_paginated_api

all_results = collect_paginated_api(
    notion.databases.query, database_id="897e5a76-ae52-4b48-9fdf-e71f5945d1af"
)
```

## Testing

Run the tests with the `pytest` command: the tests are using pytest-vcr's cassettes
for simulating requests to the Notion API.

To create new tests or run them without cassettes, you need to set up the
environment variables `NOTION_TOKEN` and `NOTION_TEST_PAGE_ID` (a page where
your integration has all the capabilities enabled).

The code will use the page at `NOTION_TEST_PAGE_ID` to generate a temporary
environment with the Notion objects to be tested, which will be deleted
at the end of the session.

## Requirements

This package supports the following minimum versions:

* Python >= 3.7
* httpx >= 0.15.0

Earlier versions may still work, but we encourage people building new applications
to upgrade to the current stable.

## Getting help

If you have a question about the library, or are having difficulty using it,
chat with the community in [GitHub Discussions](https://github.com/ramnes/notion-sdk-py/discussions).

If you're experiencing issues with the Notion API, such as a service interruption
or a potential bug in the platform, reach out to [Notion help](https://www.notion.so/Help-Support-e040febf70a94950b8620e6f00005004?target=intercom).
