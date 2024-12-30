# Quick start

Get started with notion-sdk-py in just 5 minutes!

## Setup

### Prerequisites

- Make sure you have `python` and `pip` properly installed in your system.

    ```shell
    python --version
    pip --version
    ```

- Create a new directory and move into it to follow along with this tutorial.

    ```shell
    mkdir learn-notion-sdk-py && cd learn-notion-sdk-py
    ```

### Installation

- Create a virtual environment and activate it.

    ```shell
    python -m venv .venv && source .venv/bin/activate
    ```

- Install `notion-sdk-py` using `pip`

    ```shell
    pip install --upgrade notion-client
    ```

### Integration

- Go to [notion.so/my-integrations](https://www.notion.so/my-integrations)
to create an integration. Copy the token given by Notion.

- Make it available in your environment:

    ```shell
    export NOTION_TOKEN=ntn_abcd12345
    ```

!!! tip
    Don't forget that `export` only puts the variable in the environment of the
    current shell.
    If you don't want to redo this step for every new shell,
    add the line in your shell configuration
    or use a configuration library like [dotenv](https://github.com/theskumar/python-dotenv).

## Play

Copy paste the code, and have fun tweaking it!

Let's start by initializing the client:

```python
import os
from notion_client import Client

notion = Client(auth=os.environ["NOTION_TOKEN"])
```

Let's now fetch the list of users in the scope of our integration:

```python
users = notion.users.list()

for user in users.get("results"):
    name, user_type = user["name"], user["type"]
    emoji = "😅" if user["type"] == "bot" else "🙋‍♂️"
    print(f"{name} is a {user_type} {emoji}")
```

It should output something in those lines:

```shell
Aahnik Daw is a person 🙋‍♂️
TestIntegation is a bot 😅
```

Do you see your name and the name of your integration?

🎉 Congratulations, you are now ready to use notion-sdk-py!
