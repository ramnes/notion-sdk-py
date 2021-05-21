# Quick Start

Get started with notion-sdk-py in just 5 minutes!

## Setup

### Pre requisites

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

### Create integration

- Go to [notion.so/my-integrations](https://www.notion.so/my-integrations)
to create an integration. Copy the token given by Notion.

- Make it available in your environment:

    ```shell
    export NOTION_TOKEN=secret_abcd12345
    ```

!!! tip
    Don't forget that `export` only puts the variable in the environment of the
    current shell.
    If you don't want to redo this step for every new shell,
    add the line in your shell configuration
    or use a configuration library like [dotenv](https://github.com/theskumar/python-dotenv).

## Play

Copy paste the code, and have fun tweaking it.

### Initialize the notion client

```python
from pprint import pprint
from notion_client import Client
import settings

notion = Client(auth=settings.NOTION_TOKEN)
```

### Get all users

Let us fetch the list of users in the scope of our integration.

```python
users = notion.users.list()
# print(users)

for user in users.get("results"):
    name, user_type = user["name"], user["type"]
    is_bot = user["type"] == "bot"
    print(f"{name} is a {user_type} {'😅' if is_bot else '🙋‍♂️'}")
```

This would output something in the lines of

```shell
Aahnik Daw is a person 🙋‍♂️
TestInti is a bot 😅
```

Do you see your name and the name of your integration?

🎉 Congratulations, you are now ready to use notion-sdk-py!

## Whats next ?

With the simplicity of python and flexibility of Notion,
you can connect Notion pages and databases to the tools you use every day,
creating powerful workflows.

notion-sdk-py has a lot of documentation.
A high-level overview of how it’s organized will help you know where to look for
certain things.

- **[Examples](https://github.com/ramnes/notion-sdk-py/tree/main/examples)**
Curated examples that are designed to make you learn.
- **[Reference](reference/client.md)**
Full reference of all public classes and methods.
- **[Articles](https://www.google.com/search?q=articles+related+to+notion-sdk-py)**
All articles discussing this library.
- **[Videos](https://www.youtube.com/results?search_query=notion+sdk+py)**
A list of videos that showcases related projects and tutorials.
- **[Projects](https://github.com/ramnes/notion-sdk-py/network/dependents)**
Compilation of open source projects that are using this library.
- **[Discussions](https://github.com/ramnes/notion-sdk-py/discussions)**
What people are discussing about notion-sdk-py.
