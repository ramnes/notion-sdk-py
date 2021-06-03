"""Utility functions for notion-sdk-py."""

from abc import ABC, abstractmethod
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


class ContentIterator(ABC):
    """Base class to handle pagination over content from the Notion API."""

    page: Any
    index: int

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

    @abstractmethod
    def load_next_page(self) -> Any:
        # noqa
        pass


class ResultSetIterator(ContentIterator, ABC):
    """Base class for iterating over result sets (using a cursor)."""

    cursor: Any

    def __init__(self) -> None:
        """Initialize the iterator."""
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

    @abstractmethod
    def get_page(self, params: Dict[Any, Any]) -> Any:
        # noqa
        pass


class EndpointIterator(ResultSetIterator):
    """Base class for iterating over results from an API endpoint."""

    endpoint: Any
    param: Dict[Any, Any]

    def __init__(self, endpoint: Any, **params: Any) -> None:
        super().__init__()
        self.endpoint = endpoint
        self.params = params

    def get_page(self, params: Dict[Any, Any]) -> Any:
        """Return the next page with given parameters."""
        params.update(self.params)
        return self.endpoint(**params)


class UserIterator(EndpointIterator):
    """Iterate over all users in the current workspace."""

    def __init__(self, client: "Client") -> None:
        super().__init__(client.users.list)


class DatabaseIterator(EndpointIterator):
    """Iterate over all available databases."""

    def __init__(self, client: "Client") -> None:
        super().__init__(client.databases.list)


class QueryIterator(EndpointIterator):
    """Iterate results from database queries - e.g."""

    def __init__(self, client: "Client", **query: Any) -> None:
        """
        Initialize the QueryIterator with a given query.

        This is a standard query with a database ID, filters, sorts, etc.
        """
        super().__init__(client.databases.query, **query)


class SearchIterator(EndpointIterator):
    """Iterate results from a search request - e.g."""

    def __init__(self, client: "Client", **query: Any) -> None:
        """
        Initialize the SearchIterator with a given query.

        This is a standard search query dict.
        """
        super().__init__(client.search, **query)


class ChildrenIterator(EndpointIterator):
    """Iterate over all children in a page - e.g."""

    def __init__(self, client: "Client", parent_id: str) -> None:
        """Initialize the ChildrenIterator for a given page ID."""
        super().__init__(client.blocks.children.list, block_id=parent_id)
