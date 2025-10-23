"""Notion API endpoints."""  # noqa: E501

from typing import TYPE_CHECKING, Any

from notion_client.helpers import pick
from notion_client.typing import SyncAsync

if TYPE_CHECKING:  # pragma: no cover
    from notion_client.client import BaseClient


class Endpoint:
    def __init__(self, parent: "BaseClient") -> None:
        self.parent = parent


class BlocksChildrenEndpoint(Endpoint):
    def append(self, block_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Create and append new children blocks to the block using the ID specified.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/patch-block-children)*
        """  # noqa: E501
        return self.parent.request(
            path=f"blocks/{block_id}/children",
            method="PATCH",
            body=pick(kwargs, "children", "after"),
            auth=kwargs.get("auth"),
        )

    def list(self, block_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Return a paginated array of child [block objects](https://developers.notion.com/reference/block) contained in the block.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/get-block-children)*
        """  # noqa: E501
        return self.parent.request(
            path=f"blocks/{block_id}/children",
            method="GET",
            query=pick(kwargs, "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )


class BlocksEndpoint(Endpoint):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.children = BlocksChildrenEndpoint(*args, **kwargs)

    def retrieve(self, block_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Retrieve a [Block object](https://developers.notion.com/reference/block) using the ID specified.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/retrieve-a-block)*
        """  # noqa: E501
        return self.parent.request(
            path=f"blocks/{block_id}", method="GET", auth=kwargs.get("auth")
        )

    def update(self, block_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Update the content for the specified `block_id` based on the block type.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/update-a-block)*
        """  # noqa: E501
        return self.parent.request(
            path=f"blocks/{block_id}",
            method="PATCH",
            body=pick(
                kwargs,
                "embed",
                "type",
                "archived",
                "in_trash",
                "bookmark",
                "image",
                "video",
                "pdf",
                "file",
                "audio",
                "code",
                "equation",
                "divider",
                "breadcrumb",
                "table_of_contents",
                "link_to_page",
                "table_row",
                "heading_1",
                "heading_2",
                "heading_3",
                "paragraph",
                "bulleted_list_item",
                "numbered_list_item",
                "quote",
                "to_do",
                "toggle",
                "template",
                "callout",
                "synced_block",
                "table",
                "column",
            ),
            auth=kwargs.get("auth"),
        )

    def delete(self, block_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Set a [Block object](https://developers.notion.com/reference/block), including page blocks, to `archived: true`.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/delete-a-block)*
        """  # noqa: E501
        return self.parent.request(
            path=f"blocks/{block_id}",
            method="DELETE",
            auth=kwargs.get("auth"),
        )


class DatabasesEndpoint(Endpoint):
    def retrieve(self, database_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Retrieves a [database object](https://developers.notion.com/reference/database) for a provided database ID.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/database-retrieve)*
        """  # noqa: E501
        return self.parent.request(
            path=f"databases/{database_id}",
            method="GET",
            auth=kwargs.get("auth"),
        )

    def update(self, database_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Update the title or properties of an existing database.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/update-a-database)*
        """  # noqa: E501
        return self.parent.request(
            path=f"databases/{database_id}",
            method="PATCH",
            body=pick(
                kwargs,
                "parent",
                "title",
                "description",
                "is_inline",
                "icon",
                "cover",
                "in_trash",
                "is_locked",
            ),
            auth=kwargs.get("auth"),
        )

    def create(self, **kwargs: Any) -> SyncAsync[Any]:
        """Create a new database.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/create-a-database)*
        """  # noqa: E501
        return self.parent.request(
            path="databases",
            method="POST",
            body=pick(
                kwargs,
                "parent",
                "title",
                "description",
                "is_inline",
                "initial_data_source",
                "icon",
                "cover",
            ),
            auth=kwargs.get("auth"),
        )


class DataSourcesEndpoint(Endpoint):
    def retrieve(self, data_source_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Retrieve a [data source](https://developers.notion.com/reference/data-source) object for a provided data source ID.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/retrieve-a-data-source)*
        """  # noqa: E501
        return self.parent.request(
            path=f"data_sources/{data_source_id}", method="GET", auth=kwargs.get("auth")
        )

    def query(self, data_source_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Get a list of [Pages](https://developers.notion.com/reference/page) and/or [Data Sources](https://developers.notion.com/reference/data-source) contained in the data source.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/query-a-data-source)*
        """  # noqa: E501
        return self.parent.request(
            path=f"data_sources/{data_source_id}/query",
            method="POST",
            query=pick(kwargs, "filter_properties"),
            body=pick(
                kwargs,
                "sorts",
                "filter",
                "start_cursor",
                "page_size",
                "archived",
                "in_trash",
                "result_type",
            ),
            auth=kwargs.get("auth"),
        )

    def create(self, **kwargs: Any) -> SyncAsync[Any]:
        """Add an additional [data source](https://developers.notion.com/reference/data-source) to an existing [database](https://developers.notion.com/reference/database).

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/create-a-data-source)*
        """  # noqa: E501
        return self.parent.request(
            path="data_sources",
            method="POST",
            body=pick(kwargs, "parent", "properties", "title", "icon"),
            auth=kwargs.get("auth"),
        )

    def update(self, data_source_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Updates the [data source](https://developers.notion.com/reference/data-source) object of a specified data source under a database.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/update-a-data-source)*
        """  # noqa: E501
        return self.parent.request(
            path=f"data_sources/{data_source_id}",
            method="PATCH",
            body=pick(
                kwargs, "title", "icon", "properties", "in_trash", "archived", "parent"
            ),
            auth=kwargs.get("auth"),
        )

    def list_templates(self, data_source_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """List page templates that are available for a data source.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/list-data-source-templates)*
        """  # noqa: E501
        return self.parent.request(
            path=f"data_sources/{data_source_id}/templates",
            method="GET",
            query=pick(kwargs, "name", "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )


class PagesPropertiesEndpoint(Endpoint):
    def retrieve(self, page_id: str, property_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Retrieve a `property_item` object for a given `page_id` and `property_id`.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/retrieve-a-page-property)*
        """  # noqa: E501
        return self.parent.request(
            path=f"pages/{page_id}/properties/{property_id}",
            method="GET",
            auth=kwargs.get("auth"),
            query=pick(kwargs, "start_cursor", "page_size"),
        )


class PagesEndpoint(Endpoint):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.properties = PagesPropertiesEndpoint(*args, **kwargs)

    def create(self, **kwargs: Any) -> SyncAsync[Any]:
        """Create a new page in the specified database or as a child of an existing page.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/post-page)*
        """  # noqa: E501
        return self.parent.request(
            path="pages",
            method="POST",
            body=pick(kwargs, "parent", "properties", "children", "icon", "cover"),
            auth=kwargs.get("auth"),
        )

    def retrieve(self, page_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Retrieve a [Page object](https://developers.notion.com/reference/page) using the ID specified.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/retrieve-a-page)*
        """  # noqa: E501
        return self.parent.request(
            path=f"pages/{page_id}",
            method="GET",
            query=pick(kwargs, "filter_properties"),
            auth=kwargs.get("auth"),
        )

    def update(self, page_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Update [page property values](https://developers.notion.com/reference/page#property-value-object) for the specified page.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/patch-page)*
        """  # noqa: E501
        return self.parent.request(
            path=f"pages/{page_id}",
            method="PATCH",
            body=pick(
                kwargs,
                "properties",
                "icon",
                "cover",
                "is_locked",
                "template",
                "erase_content",
                "archived",
                "in_trash",
            ),
            auth=kwargs.get("auth"),
        )


class UsersEndpoint(Endpoint):
    def list(self, **kwargs: Any) -> SyncAsync[Any]:
        """Return a paginated list of [Users](https://developers.notion.com/reference/user) for the workspace.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/get-users)*
        """  # noqa: E501
        return self.parent.request(
            path="users",
            method="GET",
            query=pick(kwargs, "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )

    def retrieve(self, user_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Retrieve a [User](https://developers.notion.com/reference/user) using the ID specified.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/get-user)*
        """  # noqa: E501
        return self.parent.request(
            path=f"users/{user_id}", method="GET", auth=kwargs.get("auth")
        )

    def me(self, **kwargs: Any) -> SyncAsync[Any]:
        """Retrieve the bot [User](https://developers.notion.com/reference/user) associated with the API token.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/get-self)*
        """  # noqa: E501
        return self.parent.request(
            path="users/me", method="GET", auth=kwargs.get("auth")
        )


class SearchEndpoint(Endpoint):
    def __call__(self, **kwargs: Any) -> SyncAsync[Any]:
        """Search all pages and child pages that are shared with the integration.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/post-search)*
        """  # noqa: E501
        return self.parent.request(
            path="search",
            method="POST",
            body=pick(kwargs, "query", "sort", "filter", "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )


class CommentsEndpoint(Endpoint):
    def create(self, **kwargs: Any) -> SyncAsync[Any]:
        """Create a new comment in the specified page or existing discussion thread.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/create-a-comment)*
        """  # noqa: E501
        return self.parent.request(
            path="comments",
            method="POST",
            body=pick(
                kwargs,
                "rich_text",
                "attachments",
                "display_name",
                "parent",
                "discussion_id",
            ),
            auth=kwargs.get("auth"),
        )

    def list(self, **kwargs: Any) -> SyncAsync[Any]:
        """Retrieve a list of un-resolved [Comment objects](https://developers.notion.com/reference/comment-object) from the specified block.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/retrieve-a-comment)*
        """  # noqa: E501
        return self.parent.request(
            path="comments",
            method="GET",
            query=pick(kwargs, "block_id", "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )


class FileUploadsEndpoint(Endpoint):
    def create(self, **kwargs: Any) -> SyncAsync[Any]:
        """Create a file upload.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/create-a-file-upload)*
        """  # noqa: E501
        return self.parent.request(
            path="file_uploads",
            method="POST",
            body=pick(
                kwargs,
                "mode",
                "filename",
                "content_type",
                "number_of_parts",
                "external_url",
            ),
            auth=kwargs.get("auth"),
        )

    def complete(self, file_upload_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Complete the file upload process.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/complete-a-file-upload)*
        """  # noqa: E501
        return self.parent.request(
            path=f"file_uploads/{file_upload_id}/complete",
            method="POST",
            auth=kwargs.get("auth"),
        )

    def retrieve(self, file_upload_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Retrieve a file upload object using the ID specified.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/retrieve-a-file-upload)*
        """  # noqa: E501
        return self.parent.request(
            path=f"file_uploads/{file_upload_id}",
            method="GET",
            auth=kwargs.get("auth"),
        )

    def list(self, **kwargs: Any) -> SyncAsync[Any]:
        """List all file uploads.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/list-file-uploads)*
        """  # noqa: E501
        return self.parent.request(
            path="file_uploads",
            method="GET",
            query=pick(kwargs, "status", "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )

    def send(self, file_upload_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Send a file upload

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/send-a-file-upload)*
        """  # noqa: E501
        return self.parent.request(
            path=f"file_uploads/{file_upload_id}/send",
            method="POST",
            form_data=pick(kwargs, "file", "part_number"),
            auth=kwargs.get("auth"),
        )
