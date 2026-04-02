"""Package notion-sdk-py.

A sync + async python client for the official Notion API.
Connect Notion pages and databases to the tools you use every day,
creating powerful workflows.
For more information visit https://github.com/ramnes/notion-sdk-py.
"""

from .client import AsyncClient, Client, RetryOptions
from .constants import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT_MS,
    DEFAULT_MAX_RETRIES,
    DEFAULT_INITIAL_RETRY_DELAY_MS,
    DEFAULT_MAX_RETRY_DELAY_MS,
    MIN_VIEW_COLUMN_WIDTH,
)
from .errors import (
    # Error codes
    NotionErrorCode,
    APIErrorCode,
    ClientErrorCode,
    # Error types
    NotionClientError,
    APIResponseError,
    UnknownHTTPResponseError,
    RequestTimeoutError,
    InvalidPathParameterError,
    # Error helpers
    is_notion_client_error,
    is_http_response_error,
)
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
    is_full_view,
    is_full_page_or_data_source,
    extract_notion_id,
    extract_database_id,
    extract_page_id,
    extract_block_id,
)

__all__ = [
    "AsyncClient",
    "Client",
    "RetryOptions",
    "DEFAULT_BASE_URL",
    "DEFAULT_TIMEOUT_MS",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_INITIAL_RETRY_DELAY_MS",
    "DEFAULT_MAX_RETRY_DELAY_MS",
    "MIN_VIEW_COLUMN_WIDTH",
    "NotionErrorCode",
    "APIErrorCode",
    "ClientErrorCode",
    "NotionClientError",
    "APIResponseError",
    "UnknownHTTPResponseError",
    "RequestTimeoutError",
    "InvalidPathParameterError",
    "is_notion_client_error",
    "is_http_response_error",
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
    "is_full_view",
    "is_full_page_or_data_source",
    "extract_notion_id",
    "extract_database_id",
    "extract_page_id",
    "extract_block_id",
]
