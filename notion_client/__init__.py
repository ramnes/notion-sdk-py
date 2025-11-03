"""Package notion-sdk-py.

A sync + async python client for the official Notion API.
Connect Notion pages and databases to the tools you use every day,
creating powerful workflows.
For more information visit https://github.com/ramnes/notion-sdk-py.
"""

from .client import AsyncClient, Client
from .errors import APIErrorCode, APIResponseError
from .helpers import (
    collect_paginated_api,
    iterate_paginated_api,
    collect_data_source_templates,
    iterate_data_source_templates,
    is_full_block,
    is_full_data_source,
    is_full_database,
    is_full_page,
    is_full_user,
    is_full_comment,
    is_full_page_or_data_source,
    extract_notion_id,
    extract_database_id,
    extract_page_id,
    extract_block_id,
)

__all__ = [
    "AsyncClient",
    "Client",
    "APIErrorCode",
    "APIResponseError",
    "collect_paginated_api",
    "iterate_paginated_api",
    "collect_data_source_templates",
    "iterate_data_source_templates",
    "is_full_block",
    "is_full_data_source",
    "is_full_database",
    "is_full_page",
    "is_full_user",
    "is_full_comment",
    "is_full_page_or_data_source",
    "extract_notion_id",
    "extract_database_id",
    "extract_page_id",
    "extract_block_id",
]
