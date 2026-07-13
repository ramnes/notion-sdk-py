# Database Email Update

Send an email notification whenever the Status of a page in a Notion database changes.

## About

This integration polls a Notion database every 5 seconds and tracks
status changes. When a page's Status property changes, it sends an
email via [SendGrid](https://sendgrid.com).

This example was built using [this database template](https://public-api-examples.notion.site/0def5dfb6d9b4cdaa907a0466834b9f4?v=aea75fc133e54b3382d12292291d9248).

## Running locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up SendGrid

Sign up for a free account at [SendGrid](https://sendgrid.com)
and create an API key.

### 3. Set up your Notion workspace

1. Create a Notion API key at [My Integrations](https://www.notion.com/my-integrations)
2. Duplicate [this database template](https://public-api-examples.notion.site/0def5dfb6d9b4cdaa907a0466834b9f4?v=aea75fc133e54b3382d12292291d9248)
3. Share the database with your integration (••• menu → Add connections)

### 4. Configure environment

Copy `.env.example` to `.env` and fill in:

```env
NOTION_KEY=<your-notion-api-key>
SENDGRID_KEY=<your-sendgrid-api-key>
NOTION_DATABASE_ID=<your-notion-database-id>
EMAIL_TO_FIELD=<recipient@example.com>
EMAIL_FROM_FIELD=<sender@example.com>
```

### 5. Run

```bash
python database_email_update.py
```

The script will poll every 5 seconds and send emails on status changes.
