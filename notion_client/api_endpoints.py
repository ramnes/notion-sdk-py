"""Notion API endpoints."""

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

        Returns the Block object which contains the new children.
        """
        return self.parent.request(
            path=f"blocks/{block_id}/children",
            method="PATCH",
            body=pick(kwargs, "children"),
            auth=kwargs.get("auth"),
        )

    def list(self, block_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Return a paginated array of child block objects contained in the block.

        In order to receive a complete representation of a block, you may need to
        recursively retrieve the block children of child blocks.
        """
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
        """Retrieve a Block object using the ID specified."""
        return self.parent.request(
            path=f"blocks/{block_id}", method="GET", auth=kwargs.get("auth")
        )

    def update(self, block_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Update the content for the specified `block_id` based on the block type.

        Supported fields are based on the block object type.

        **Note**: The update replaces the *entire* value for a given field. If a field is
        omitted (ex: omitting `checked` when updating a `to_do` block), the value will
        not be changed.

        Currently this endpoint supports updating `paragraph`, `heading_1`, `heading_2`,
        `heading_3`, `bulleted_list_item`, `numbered_list_item`, `toggle` and `to_do`
        blocks.
        """
        return self.parent.request(
            path=f"blocks/{block_id}",
            method="PATCH",
            body=pick(
                kwargs,
                "heading_1",
                "type",
                "archived",
                "heading_2",
                "heading_3",
                "embed",
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
                "paragraph",
                "bulleted_list_item",
                "numbered_list_item",
                "quote",
                "to_do",
                "toggle",
                "template",
                "callout",
                "synced_block",
            ),
            auth=kwargs.get("auth"),
        )

    def delete(self, block_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Set a Block object, including page blocks, to `archived: true`.

        **Note**: in the Notion UI application, this moves the block to the "Trash" where
        it can still be accessed and restored.
        """
        return self.parent.request(
            path=f"blocks/{block_id}",
            method="DELETE",
            auth=kwargs.get("auth"),
        )


class DatabasesEndpoint(Endpoint):
    def list(self, **kwargs: Any) -> SyncAsync[Any]:
        """List all Databases shared with the authenticated integration.

        > ⚠️  **Search pages for more details**
        >
        > This endpoint is no longer recommended, use search instead. This endpoint will
        > only return explicitly shared pages, while search will also return child pages
        > within explicitly shared pages. This endpoint's results cannot be filtered,
        > while search can be used to match on page title.
        """
        return self.parent.request(
            path="databases",
            method="GET",
            query=pick(kwargs, "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )

    def query(self, database_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Get a list of Pages contained in the database.

        The result is filtered and ordered according to the filter conditions and sort
        criteria provided in the request.
        """
        return self.parent.request(
            path=f"databases/{database_id}/query",
            method="POST",
            body=pick(kwargs, "filter", "sorts", "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )

    def retrieve(self, database_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Retrieve a Database object using the ID specified."""
        return self.parent.request(
            path=f"databases/{database_id}", method="GET", auth=kwargs.get("auth")
        )

    def create(self, **kwargs: Any) -> SyncAsync[Any]:
        """Create a database as a subpage in the specified parent page."""
        return self.parent.request(
            path="databases",
            method="POST",
            body=pick(kwargs, "parent", "title", "properties", "icon", "cover"),
            auth=kwargs.get("auth"),
        )

    def update(self, database_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Update an existing database as specified by the parameters."""
        return self.parent.request(
            path=f"databases/{database_id}",
            method="PATCH",
            body=pick(kwargs, "properties", "title", "icon", "cover"),
            auth=kwargs.get("auth"),
        )


class PagesPropertiesEndpoint(Endpoint):
    def retrieve(self, page_id: str, property_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Retrieve a `property_item` object for a given `page_id` and `property_id`.

        Depending on the property type, the object returned will either be a value or a
        paginated list of property item values.
        """
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

        If the parent is a database, the `properties` parameter must conform to the
        parent database's property schema.

        If the parent is a page, the only valid property is `title`. The new page may
        include page content, described as blocks in the `children` parameter.
        """
        return self.parent.request(
            path="pages",
            method="POST",
            body=pick(kwargs, "parent", "properties", "children", "icon", "cover"),
            auth=kwargs.get("auth"),
        )

    def retrieve(self, page_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Retrieve a Page object using the ID specified."""
        return self.parent.request(
            path=f"pages/{page_id}", method="GET", auth=kwargs.get("auth")
        )

    def update(self, page_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Update page property values for the specified page.

        Properties that are not set via the `properties` parameter will remain
        unchanged.  If the parent is a database, the new property values in the
        `properties` parameter must conform to the parent database's property schema.
        """
        return self.parent.request(
            path=f"pages/{page_id}",
            method="PATCH",
            body=pick(kwargs, "archived", "properties", "icon", "cover"),
            auth=kwargs.get("auth"),
        )


class UsersEndpoint(Endpoint):
    def list(self, **kwargs: Any) -> SyncAsync[Any]:
        """Return a paginated list of Users for the workspace."""
        return self.parent.request(
            path="users",
            method="GET",
            query=pick(kwargs, "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )

    def retrieve(self, user_id: str, **kwargs: Any) -> SyncAsync[Any]:
        """Retrieve a User using the ID specified."""
        return self.parent.request(
            path=f"users/{user_id}", method="GET", auth=kwargs.get("auth")
        )

    def me(self, **kwargs: Any) -> SyncAsync[Any]:
        """Retrieve the bot User associated with the API token.

        The bot will have an owner field with information about the person who authorized
        the integration.
        """
        return self.parent.request(
            path="users/me", method="GET", auth=kwargs.get("auth")
        )


class SearchEndpoint(Endpoint):
    def __call__(self, **kwargs: Any) -> SyncAsync[Any]:
        """Search all pages and child pages that are shared with the integration.

        The results may include databases. The `query` parameter matches against the page
        titles. If the `query` parameter is not provided, the response will contain all
        pages (and child pages) in the results.

        The `filter` parameter can be used to query specifically for only pages or only
        databases.
        """
        return self.parent.request(
            path="search",
            method="POST",
            body=pick(kwargs, "query", "sort", "filter", "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )
