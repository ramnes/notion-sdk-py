# Parse text from any block type

Extract plain text from any type of Notion block,
including headers, lists, media, and more.

## About

This example retrieves
[page content](https://developers.notion.com/docs/working-with-page-content)
(represented as
[blocks](https://developers.notion.com/docs/working-with-page-content#modeling-content-as-blocks))
and extracts plain text from each block. The text is printed to the
console, but can be used in your projects as needed.

When retrieving block children with the public API,
the block structure varies by type. This example handles the
different block shapes and extracts available text in a uniform way.

**Note:** Not all blocks contain text (e.g., dividers),
and some block types may not yet be supported by the public API.

## Running locally

### 1. Install dependencies

```bash
pip install notion-client
```

Optionally install `python-dotenv` to load environment variables from a `.env` file:

```bash
pip install python-dotenv
```

### 2. Set up your Notion integration

1. Create a new integration in the [integrations dashboard](https://www.notion.com/my-integrations)
2. Copy the API key ("Internal Integration Token") from the Secrets page

### 3. Set environment variables

Copy `.env.example` to `.env` and fill in your values:

```env
NOTION_API_KEY=<your-notion-api-key>
NOTION_PAGE_ID=<notion-page-id>
```

The page ID is the 32-character string at the end of any Notion page URL:
`https://www.notion.so/My-Page-<page_id>`

### 4. Share the page with your integration

1. Open the page in Notion
2. Click the `•••` menu in the top-right corner
3. Scroll down and click `Add connections`
4. Search for and select your integration

### 5. Run the script

```bash
python parse_text_from_any_block_type.py
```
