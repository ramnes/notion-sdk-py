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
    def list(self, **kwargs: Any) -> SyncAsync[Any]:  # pragma: no cover
        """List all [Databases](https://developers.notion.com/reference/database) shared with the authenticated integration.

        > ⚠️  **Deprecated endpoint**

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/get-databases)*
        """  # noqa: E501
        return self.parent.request(
            path="databases",
            method="GET",
            query=pick(kwargs, "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )

    def query(self, database_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Query a database (legacy) or route to data source under 2025-09-03.

        - For Notion-Version >= 2025-09-03, require `data_source_id` and route to
          `data_sources.query`.
        - For legacy versions, call the databases query endpoint.
        """
        new_api = getattr(self.parent.options, "notion_version", "") >= "2025-09-03"
        data_source_id = kwargs.get("data_source_id")
        if new_api and data_source_id:
            _kwargs = dict(kwargs)
            _kwargs.pop("data_source_id", None)
            return self.parent.data_sources.query(
                data_source_id=data_source_id, **_kwargs
            )

        return self.parent.request(
            path=f"databases/{database_id}/query",
            method="POST",
            query=pick(kwargs, "filter_properties"),
            body=pick(
                kwargs,
                "filter",
                "sorts",
                "start_cursor",
                "page_size",
                "archived",
                "in_trash",
            ),
            auth=kwargs.get("auth"),
        )

    def retrieve(self, database_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Retrieve a [Database object](https://developers.notion.com/reference/database) using the ID specified.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/retrieve-a-database)*
        """  # noqa: E501
        return self.parent.request(
            path=f"databases/{database_id}", method="GET", auth=kwargs.get("auth")
        )

    def create(self, **kwargs: Any) -> SyncAsync[Any]:
        """Create a database (and initial data source under 2025-09-03).

        For Notion-Version >= 2025-09-03, schema `properties` should be moved under
        `initial_data_source.properties`. This method adapts automatically if only
        `properties` is provided.
        """
        body = pick(
            kwargs,
            "parent",
            "title",
            "description",
            "properties",
            "initial_data_source",
            "icon",
            "cover",
            "is_inline",
        )
        new_api = getattr(self.parent.options, "notion_version", "") >= "2025-09-03"
        if new_api:
            if "initial_data_source" not in body and "properties" in body:
                # Move properties under initial_data_source
                props = body.pop("properties")
                body["initial_data_source"] = {"properties": props}
            # If both were provided, prefer explicit initial_data_source
            if "properties" in body:
                body.pop("properties", None)
        return self.parent.request(
            path="databases",
            method="POST",
            body=body,
            auth=kwargs.get("auth"),
        )

    def update(self, database_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Update a database. For schema changes under 2025-09-03, use data source update.

        If `properties` are supplied and Notion-Version >= 2025-09-03, you must
        also provide `data_source_id`, and this method will dispatch to
        `client.data_sources.update`. Remaining top-level database fields are
        patched via the database update API.
        """
        new_api = getattr(self.parent.options, "notion_version", "") >= "2025-09-03"
        body = pick(
            kwargs,
            "properties",
            "title",
            "description",
            "icon",
            "cover",
            "is_inline",
            "archived",
            "in_trash",
            "parent",
        )

        responses = None
        if new_api and "properties" in body:
            data_source_id = kwargs.get("data_source_id")
            if not data_source_id:
                raise ValueError(
                    "To update schema under 2025-09-03, supply data_source_id and "
                    "use Data Sources update."
                )
            # Dispatch properties (and optional title) to the data source update
            ds_payload = pick(kwargs, "properties", "title", "in_trash")
            responses = self.parent.data_sources.update(data_source_id, **ds_payload)
            # Remove properties from database-level update
            body.pop("properties", None)

        # If anything remains to patch at the database level, do it
        if any(k in body for k in body.keys()):
            db_resp = self.parent.request(
                path=f"databases/{database_id}",
                method="PATCH",
                body=body,
                auth=kwargs.get("auth"),
            )
            return db_resp if responses is None else db_resp

        # Only data source update was needed
        return responses


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
            body=pick(kwargs, "in_trash", "archived", "properties", "icon", "cover"),
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
        body = pick(kwargs, "query", "sort", "filter", "start_cursor", "page_size")
        # Under 2025-09-03, filter.object value "database" becomes "data_source"
        new_api = getattr(self.parent.options, "notion_version", "") >= "2025-09-03"
        filt = body.get("filter") if isinstance(body.get("filter"), dict) else None
        if new_api and filt and filt.get("property") == "object":
            val = filt.get("value")
            if val == "database":
                filt["value"] = "data_source"
                self.parent.logger.warning(
                    "Search filter.value 'database' is deprecated; using 'data_source'."
                )
        return self.parent.request(
            path="search",
            method="POST",
            body=body,
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


class DataSourcesEndpoint(Endpoint):
    def create(self, **kwargs: Any) -> SyncAsync[Any]:
        """Create a new data source under an existing database.

        Expects a database parent and the data source schema `properties`.
        """
        return self.parent.request(
            path="data_sources",
            method="POST",
            body=pick(
                kwargs,
                "parent",  # {"type": "database_id", "database_id": "..."}
                "properties",  # schema definition for this data source
                "title",  # optional display title for the data source
            ),
            auth=kwargs.get("auth"),
        )

    def retrieve(self, data_source_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Retrieve a Data Source object using the ID specified.

        [🔗 Endpoint documentation](/reference/retrieve-a-data-source)
        """
        return self.parent.request(
            path=f"data_sources/{data_source_id}",
            method="GET",
            auth=kwargs.get("auth"),
        )

    def query(self, data_source_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Query a data source.

        [🔗 Endpoint documentation](/reference/query-a-data-source)
        """
        return self.parent.request(
            path=f"data_sources/{data_source_id}/query",
            method="POST",
            query=pick(kwargs, "filter_properties"),
            body=pick(
                kwargs,
                "filter",
                "sorts",
                "start_cursor",
                "page_size",
                "archived",
                "in_trash",
            ),
            auth=kwargs.get("auth"),
        )

    def update(self, data_source_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Update attributes of a data source such as schema properties and title.

        [🔗 Endpoint documentation](/reference/update-a-data-source)
        """
        return self.parent.request(
            path=f"data_sources/{data_source_id}",
            method="PATCH",
            body=pick(
                kwargs,
                "properties",
                "title",
                "in_trash",
            ),
            auth=kwargs.get("auth"),
        )
