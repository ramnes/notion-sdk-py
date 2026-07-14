# Web form with Flask

Use web forms to create new Notion databases, pages, page content, and comments.

## About

This example shows how to build an internal integration that allows users to
fill out a web form to create new Notion databases, pages, blocks, and comments.
It uses the Flask web framework and serves a browser-based UI.

### Notion endpoints used

- [Create a database](https://developers.notion.com/reference/create-a-database)
- [Create a page](https://developers.notion.com/reference/post-page)
- [Append block children](https://developers.notion.com/reference/patch-block-children)
- [Create a comment](https://developers.notion.com/reference/create-a-comment)

## Running locally

### 1. Install dependencies

```bash
pip install notion-client flask python-dotenv
```

### 2. Set up your integration

1. Create a new integration in the [integrations dashboard](https://www.notion.com/my-integrations)
2. Copy the API key from the `Secrets` page
3. Enable read and write comment capabilities in the `Capabilities` tab

### 3. Get your page ID

The page ID is the 32-character string at the end of any Notion page URL:
`https://www.notion.so/My-Page-<page_id>`

### 4. Set environment variables

Copy `.env.example` to `.env` and fill in your values.

### 5. Share the page with your integration

1. Open the page in Notion
2. Click `...` > `Add connections`
3. Search for and select your integration

### 6. Run the app

```bash
python web_form_with_flask.py
```

Open `http://localhost:3000` in your browser.
