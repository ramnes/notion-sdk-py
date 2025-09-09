# Examples

This section contains several single-file examples using [notion-sdk-py].

Read the [Quick Start](/docs/user_guides/quick_start.md) before you come here.

## Note for 2025-09-03 API

Starting with Notion API version 2025-09-03, most database-scoped
operations happen at the data source level. Examples that create pages
under a database now set the parent using a `data_source_id` instead of
`database_id`.

- If you have a `NOTION_DATABASE_ID`, the examples resolve the matching
  `data_source_id` via `databases.retrieve(...).data_sources[0].id`.
- When querying, prefer `client.data_sources.query(data_source_id=...)`.

See New API notes in `NewApi_250903.md` at the repository root for a
complete migration guide.

## Downloading

You may download all.

```shell
git clone https://github.com/ramnes/notion-sdk-py
cd notion-sdk-py/examples
ls # list all examples
```

All examples are licensed under the [CC0 License](https://creativecommons.org/choose/zero/),
so you can use them as the base for your own code without worrying about copyright.
