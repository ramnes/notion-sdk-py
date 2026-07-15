# Notion-GitHub issue sync

Sync GitHub issues for a specific repository to a Notion Database.

## About

This example fetches issues from a GitHub repository and creates or updates
corresponding pages in a Notion database. Changes made to issues in the
Notion database will not be reflected back to GitHub.

## Running locally

### 1. Install dependencies

```bash
pip install notion-client requests python-dotenv
```

### 2. Set up your integrations

1. Create a new integration in the [integrations dashboard](https://www.notion.com/my-integrations)
2. Copy the API key
3. Create a [GitHub personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

### 3. Prepare your Notion database

Create a new Notion database (full page, not inline) with the following properties:

| Property name      | Type   |
|--------------------|--------|
| Name               | Title  |
| Issue Number       | Number |
| State              | Select |
| Number of Comments | Number |
| Issue URL          | URL    |

Share the database with your integration (click `...` > `Add connections`).

### 4. Set environment variables

Copy `.env.example` to `.env` and fill in your values:

```env
NOTION_API_KEY=<your-notion-api-key>
NOTION_DATABASE_ID=<notion-database-id>
GITHUB_TOKEN=<your-github-personal-access-token>
GITHUB_REPO_OWNER=<github-owner-username>
GITHUB_REPO_NAME=<github-repo-name>
```

### 5. Run the script

```bash
python notion_github_sync.py
```
