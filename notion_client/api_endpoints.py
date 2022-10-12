"""Notion API endpoints."""  # noqa: E501

from typing import TYPE_CHECKING, Any

from notion_client.helpers import pick
from notion_client.typing import SyncAsync

if TYPE_CHECKING:
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
            body=pick(kwargs, "children"),
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
    def list(self, **kwargs: Any) -> SyncAsync[Any]:
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
        """Get a list of [Pages](https://developers.notion.com/reference/page) contained in the database.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/post-database-query)*
        """  # noqa: E501
        return self.parent.request(
            path=f"databases/{database_id}/query",
            method="POST",
            body=pick(kwargs, "filter", "sorts", "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )

    def retrieve(self, database_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Retrieve a [Database object](https://developers.notion.com/reference/database) using the ID specified.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/post-database-query)*
        """  # noqa: E501
        return self.parent.request(
            path=f"databases/{database_id}", method="GET", auth=kwargs.get("auth")
        )

    def create(self, **kwargs: Any) -> SyncAsync[Any]:
        """Create a database as a subpage in the specified parent page.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/create-a-database)*
        """  # noqa: E501
        return self.parent.request(
            path="databases",
            method="POST",
            body=pick(kwargs, "parent", "title", "properties", "icon", "cover", "is_inline"),
            auth=kwargs.get("auth"),
        )

    def update(self, database_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Update an existing database as specified by the parameters.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/update-a-database)*
        """  # noqa: E501
        return self.parent.request(
            path=f"databases/{database_id}",
            method="PATCH",
            body=pick(kwargs, "properties", "title", "icon", "cover"),
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
            path=f"pages/{page_id}", method="GET", auth=kwargs.get("auth")
        )

    def update(self, page_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Update [page property values](https://developers.notion.com/reference/page#property-value-object) for the specified page.

        *[🔗 Endpoint documentation](https://developers.notion.com/reference/patch-page)*
        """  # noqa: E501
        return self.parent.request(
            path=f"pages/{page_id}",
            method="PATCH",
            body=pick(kwargs, "archived", "properties", "icon", "cover"),
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
            body=pick(kwargs, "parent", "discussion_id", "rich_text"),
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
