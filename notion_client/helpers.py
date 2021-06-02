"""Utility functions for notion-sdk-py."""

from typing import TYPE_CHECKING, Any, Dict, Iterator
from urllib.parse import urlparse
from uuid import UUID

if TYPE_CHECKING:
    from notion_client.client import Client

CONTENT_PAGE_SIZE = 100


def pick(base: Dict[Any, Any], *keys: str) -> Dict[Any, Any]:
    """Return a Dict composed of key value pairs for keys passed as args."""
    return {key: base[key] for key in keys if key in base}


def get_url(obj_id: str) -> str:
    """Return url for the object of given id."""
    uuid = UUID(obj_id).hex
    return "https://notion.so/" + uuid


def get_id(url: str) -> str:
    """Return the id of the object of given url."""
    parsed = urlparse(url)
    if parsed.netloc != "notion.so":
        raise ValueError("Not a valid Notion URL")
    path = parsed.path
    if len(path) < 32:
        raise ValueError("The path in the URL seems to be incorrect.")
    raw_id = path[-32:]
    return str(UUID(raw_id))


class ContentIterator(object):
    """Base class to handle pagination over content from the Notion API."""

    page: Any
    client: "Client"
    index: int

    def __init__(self, client: "Client") -> None:
        """Initialize the interator using the specified client for requests."""
        self.client = client

    def __iter__(self) -> Iterator[Any]:
        """Initialize the iterator."""
        self.page = None
        self.index = -1

        return self

    def __next__(self) -> Any:
        """Return the next item from the result set or StopIteration."""
        # load a new page if needed
        if self.page is None or self.index >= len(self.page):
            self.index = 0
            self.page = self.load_next_page()

        # if we have run out of results...
        if self.page is None or len(self.page) == 0:
            raise StopIteration

        # pull the next item from the current page
        item = self.page[self.index]

        # setup for the next call
        self.index += 1

        return item

    def load_next_page(self) -> Any:
        """Must be implemented in subclasses.

        Returns the next page of content or None.
        """
        raise ValueError


class ResultSetIterator(ContentIterator):
    """Base class for iterating over result sets (using a cursor)."""

    cursor: Any

    def __init__(self, client: "Client") -> None:
        super().__init__(client)
        self.cursor = None

    def load_next_page(self) -> Any:
        """Return the next page of content."""
        if self.cursor is False:
            return None

        params = {"page_size": CONTENT_PAGE_SIZE}

        if self.cursor:
            params["start_cursor"] = self.cursor

        # TODO error checking on result
        result = self.get_page(params)

        if result["has_more"]:
            self.cursor = result["next_cursor"]
        else:
            self.cursor = False

        return result["results"]

    def get_page(self, params: Dict[Any, Any]) -> Any:
        """Must be implemented in subclasses.

        Returns the page starting at cursor or None.
        """
        raise ValueError


class UserIterator(ResultSetIterator):
    """Iterate over all users in the current workspace.

    for db in UserIterator(client):
        ...
    """

    def get_page(self, params: Dict[Any, Any]) -> Any:
        """Return the next page with given parameters."""
        return self.client.users.list(**params)


class DatabaseIterator(ResultSetIterator):
    """Iterate over all available databases.

    for db in DatabaseIterator(client):
        ...
    """

    def get_page(self, params: Dict[Any, Any]) -> Any:
        """Return the next page with given parameters."""
        return self.client.databases.list(**params)


class QueryIterator(ResultSetIterator):
    """Iterate results from database queries - e.g.

    issues = QueryIterator(client, {
        'database_id': issue_db,
        'sorts' : [{
            'direction': 'ascending',
            'property': 'Last Update'
        }]
    })

    for issue in issues:
        ...
    """

    def __init__(self, client: "Client", query: Dict[Any, Any]) -> None:
        """
        Initialize the QueryIterator with a given query.

        This is a standard query with a database ID, filters, sorts, etc.
        """
        super().__init__(client)
        self.query = query

    def get_page(self, params: Dict[Any, Any]) -> Any:
        """Return the next page with given parameters."""
        # add our query to the params and execute...
        params.update(self.query)

        return self.client.databases.query(**params)


class SearchIterator(ResultSetIterator):
    """Iterate results from a search request - e.g.

    search = SearchIterator(client, {
        'query' : 'tasks',
        'sort' : {
            'direction': 'ascending',
            'timestamp': 'last_edited_time'
        }
    })

    for item in search:
        ...
    """

    def __init__(self, client: "Client", query: Dict[Any, Any]) -> None:
        """
        Initialize the SearchIterator with a given query.

        This is a standard search query dict.
        """
        super().__init__(client)
        self.query = query

    def get_page(self, params: Dict[Any, Any]) -> Any:
        """Return the next page with given parameters."""
        # add our query to the params and execute...
        params.update(self.query)

        return self.client.search(**params)


class BlockChildrenIterator(ResultSetIterator):
    """Iterate over all children in a page - e.g.

    for child in BlockChildrenIterator(client, page_id):
        ...
    """

    def __init__(self, client: "Client", parent_id: str) -> None:
        """Initialize the BlockChildrenIterator for a given page ID."""
        super().__init__(client)
        self.parent_id = parent_id

    def get_page(self, params: Dict[Any, Any]) -> Any:
        """Return the next page with given parameters."""
        # add our parent ID to the params and execute...
        params["block_id"] = self.parent_id

        return self.client.blocks.children.list(**params)
