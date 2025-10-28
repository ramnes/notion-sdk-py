# Generate Random Data Example

## Overview

Populate any Notion database with realistic test data. This example
automatically detects your database schema and generates appropriate fake data
for each property type.

## Setup

### 1. Clone and install

```bash
# Clone this repository locally
git clone https://github.com/ramnes/notion-sdk-py.git

# Switch into this project
cd notion-sdk-py/examples/generate_random_data

# Install the dependencies
pip install -r requirements.txt
```

### 2. Create a Notion integration

1. Visit [My Integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Give it a name and save
4. Copy the integration token

### 3. Share a database with your integration

1. Open any database in Notion
2. Click "..." menu → "Add connections"
3. Search for and add your integration

### 4. Configure and run

```bash
# Set your integration token (or add to .env file)
export NOTION_TOKEN=your-integration-token

# Run the script
python generate_random_data.py
```

## Features

- Detects database schema automatically
- Creates 10 test entries with realistic data
- Shows filtering and querying examples

## Property Types

- Title & Rich Text
- Number
- Select & Multi-select
- Date
- Checkbox
- URL, Email, Phone Number
- Files (as external URLs)
