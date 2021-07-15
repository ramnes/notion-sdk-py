"""Utility functions for notion-sdk-py."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator
from urllib.parse import urlparse
from uuid import UUID

CONTENT_PAGE_SIZE = 100


def pick(base: Dict[Any, Any], *keys: str) -> Dict[Any, Any]:
    """Return a dict composed of key value pairs for keys passed as args."""
    return {key: base[key] for key in keys if key in base}


def get_url(object_id: str) -> str:
    """Return the URL for the object with the given id."""
    return "https://notion.so/" + UUID(object_id).hex


def get_id(url: str) -> str:
    """Return the id of the object behind the given URL."""
    parsed = urlparse(url)
    if parsed.netloc != "notion.so":
        raise ValueError("Not a valid Notion URL.")
    path = parsed.path
    if len(path) < 32:
        raise ValueError("The path in the URL seems to be incorrect.")
    raw_id = path[-32:]
    return str(UUID(raw_id))


class ContentIterator(ABC):
    """Base class to handle pagination over content from the Notion API."""

    page: Any
    index: int
    pagenum: int

    def __iter__(self) -> Iterator[Any]:
        """Initialize the iterator."""
        self.page = None
        self.index = -1
        self.pagenum = 0

        return self

    def __next__(self) -> Any:
        """Return the next item from the result set or raise StopIteration."""
        # load a new page if needed
        if self.page is None or self.index >= len(self.page):
            self.index = 0
            self.page = self.load_next_page()
            self.pagenum += 1

        # if we have run out of results...
        if self.page is None or len(self.page) == 0:
            raise StopIteration

        # pull the next item from the current page
        item = self.page[self.index]

        # setup for the next call
        self.index += 1

        return item

    @property
    def page_number(self) -> int:
        """Return the current page number of results in this iterator."""
        return self.pagenum

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

    @property
    def last_page(self) -> bool:
        """Return true if this is the last page of results."""
        if self.cursor is None:
            raise ValueError("iterator has not been initialized")

        return self.cursor is False

    @abstractmethod
    def get_page(self, params: Dict[str, Any]) -> Any:
        # noqa
        pass


class EndpointIterator(ResultSetIterator):
    """Base class for iterating over results from an API endpoint."""

    endpoint: Any  # should be Callable - https://github.com/python/mypy/issues/708
    params: Dict[Any, Any]

    def __init__(self, endpoint: Any, **params: Any) -> None:
        super().__init__()
        self.endpoint = endpoint
        self.params = params

    # XXX should return Dict[str, Any] from Callable[[Any], Dict[str, Any]]
    def get_page(self, params: Dict[str, Any]) -> Any:
        """Return the next page with given parameters."""
        params.update(self.params)
        return self.endpoint(**params)
