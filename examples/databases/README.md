# Create a database

This example shows how to create a new database inside an existing Notion page.

## Content of the example

The `manual_inputs` function is used to collect the page ID and
the name of the target database.

*Enter the ID or the URL of the page in which you want to create the database:*

The URL of the parent page or its ID can be entered here.

*Name of the database that you want to create:*

Provide the name of the newly created database.

The `create_database`function defines the property of the database.

*Note*: when creating a database, a property of type *title* is always required.

## Execute test

Your NOTION_TOKEN must be defined in as an environment variable.
If not, a prompt will ask you for it.

### Install notion-client

<!-- markdownlint-disable -->
```shell
pip install notion-client
```

### Run the test

<!-- markdownlint-disable -->
```shell
python create_database.py
```
