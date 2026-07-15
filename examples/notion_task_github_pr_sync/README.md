# Sync closed GitHub PRs to Notion tasks

Connect pull requests to the Notion tasks they implement. When a linked PR is
closed, this example adds the outcome to its Notion task and can optionally
update a Status property.

The script reads one GitHub repository and writes only to Notion. It does not
change pull requests or other GitHub data.

## Running locally

### 1. Install dependencies

```bash
pip install notion-client requests python-dotenv
```

### 2. Set up your integrations

1. Create a new integration in the [integrations dashboard](https://www.notion.com/my-integrations)
   and connect it to your task database through `...` > `Add connections`.
2. Create a [GitHub personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
   with read access to pull requests.

### 3. Link PRs to Notion tasks

For a PR to match a task, put the task's canonical Notion page URL at the end
of the PR description, without query parameters:

```text
https://www.notion.so/{your-task-id}
```

### 4. Set environment variables

Copy `.env.example` to `.env` and fill in your values.

### 5. Run the script

```bash
python notion_task_github_pr_sync.py
```
