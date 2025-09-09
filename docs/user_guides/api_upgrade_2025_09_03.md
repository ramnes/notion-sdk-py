---
title: API Upgrade (2025-09-03)
---

The SDK targets Notion API version 2025-09-03. This release introduces
data sources under databases and moves most database-scoped operations to
the `/v1/data_sources` namespace.

Key points:

- Use a `data_source_id` when creating pages with a database parent:
  `parent={"type": "data_source_id", "data_source_id": "..."}`.
- Query via `client.data_sources.query(data_source_id=...)`.
- Create a new data source for an existing database with
  `client.data_sources.create(...)`.
- When creating a database, put the schema under
  `initial_data_source.properties`.

Examples:

- First project, updated to use data sources:
  `examples/first_project/script.py`.
- Create a data source under an existing database:
  `examples/databases/create_data_source.py`.

For a full migration guide, see `NewApi_250903.md` at the repository root.
