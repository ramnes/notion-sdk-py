<div align="center">
	<h1>Notion SDK for Python</h1>
	<p>
		<b>A simple and easy to use client for the <a href="https://developers.notion.com">Notion API</a></b>
	</p>
	<br>
	<br>
	<br>
</div>

This client is meant to be a Python version of the reference [JavaScript SDK](https://github.com/makenotion/notion-sdk-js), so usage should be pretty similar between both. :blush:

> :warning: Big work in progress, pull requests are more than welcome!

## Installation

```
pip install notionhq-client
```

## Usage

> Before getting started, [create an integration](https://www.notion.com/my-integrations) and find the token.
>
> [→ Learn more about authorization](https://developers.notion.com/docs/authorization).

Import and initialize a client using an **integration token** or an OAuth **access token**.

```python
import os
from notionhq_client import Client

notion = Client(auth=os.environ["NOTION_TOKEN"])
```

Make a request to any Notion API endpoint.

> See the complete list of endpoints in the [API reference](https://developers.notion.com/reference).

```python
from pprint import pprint

list_users_response = notion.users.list()
pprint(list_users_response.json())
```

This would output something like:

```
{'results': [{'avatar_url': 'https://secure.notion-static.com/e6a352a8-8381-44d0-a1dc-9ed80e62b53d.jpg',
              'id': 'd40e767c-d7af-4b18-a86d-55c61f1e39a4',
              'name': 'Avocado Lovelace',
              'object': 'user',
              'person': {'email': 'avo@example.org'},
              'type': 'person'},
             ...]}
```

Endpoint parameters are grouped into a single object. You don't need to remember which parameters go in the path, query, or body.

```python
my_page = notion.databases.query(
    **{
        "database_id": "897e5a76-ae52-4b48-9fdf-e71f5945d1af",
        "filter": {
            "property": "Landmark",
            "text": {
                "contains": "Bridge",
            },
        },
    }
)
```

### Handling errors

If the API returns an unsuccessful response, an `APIResponseError` will be raised.

The error contains properties from the response, and the most helpful is `code`. You can compare `code` to the values in the `APIErrorCode` object to avoid misspelling error codes.

```python
import logging
from notionhq_client import APIErrorCode, APIResponseError

try:
    my_page = notion.databases.query(
        **{
            "database_id": "897e5a76-ae52-4b48-9fdf-e71f5945d1af",
            "filter": {
                "property": "Landmark",
                "text": {
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
        logging.exception()
```

### Logging

The client emits useful information to a logger. By default, it only emits warnings and errors.

If you're debugging an application, and would like the client to log response bodies, set the `log_level` option to `logging.DEBUG`.

```python
notion = Client(
    auth=os.environ["NOTION_TOKEN"],
    log_level=logging.DEBUG,
)
```

You may also set a custom `logger` to emit logs to a destination other than `stdout`. Have a look at [Python's logging cookbook](https://docs.python.org/3/howto/logging-cookbook.html) if you want to create your own logger.

### Client options

The `Client` supports the following options on initialization. These options are all keys in the single constructor parameter.

| Option | Default value | Type | Description |
|--------|---------------|---------|-------------|
| `auth` | `None` | `string` | Bearer token for authentication. If left undefined, the `auth` parameter should be set on each request. |
| `log_level` | `logging.WARNING` | `int` | Verbosity of logs the instance will prodice. By default, logs are written to `stdout`.
| `timeoutMs` | `60_000` | `int` | Number of milliseconds to wait before emitting a `RequestTimeoutError` |
| `base_url` | `"https://api.notion.com"` | `string` | The root URL for sending API requests. This can be changed to test with a mock server. |
| `logger` | Log to console | `logging.Logger` | A custom logger. |

## Requirements

This package supports the following minimum versions:
* Python >= 3.6
* httpx >= 0.15.0

Earlier versions may still work, but we encourage people building new applications to upgrade to the current stable.

## Getting help

If you have a question about the library, or are having difficulty using it, chat with the community in [GitHub Discussions](https://github.com/ramnes/notion-sdk-py/discussions).

If you're experiencing issues with the Notion API, such as a service interruption or a potential bug in the platform, reach out to [Notion help](https://www.notion.so/Help-Support-e040febf70a94950b8620e6f00005004?target=intercom).
