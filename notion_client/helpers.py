"""Utility functions for notion-sdk-py."""


from typing import Any, Dict
from urllib.parse import urlparse
from uuid import UUID

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

""" base class to handle pagination support """
class ContentIterator(object):

    def __init__(self, client):
        self.client = client

    def __iter__(self):
        self.page = None
        self.index = 0

        return self

    def __next__(self):
        # load a new page if needed
        if self.page is None or self.index >= len(self.page):
            self.index = 0
            self.page = self.next_page()

        # if we have run out of results...
        if self.page is None:
            raise StopIteration

        # pull the next item from the current page
        item = self.page[self.index]

        # setup for the next call
        self.index += 1

        return item

    def next_page(self): raise ValueError

""" paginate database queries - e.g.

    issues = DatabaseIterator(client, {
        'database_id': issue_db,
        'sorts' : [{
            'direction': 'ascending',
            'property': 'Last Update'
        }]
    })

    for issue in issues:
        ...
"""
class DatabaseIterator(ContentIterator):

    def __init__(self, client, query):
        ContentIterator.__init__(self, client)
        self.query = query
        self.cursor = None

    def next_page(self):
        if self.cursor is False:
            return None

        params = self.query
        params['page_size'] = CONTENT_PAGE_SIZE

        if self.cursor:
            params['start_cursor'] = self.cursor

        # TODO error checking on result
        result = self.client.databases.query(**params)

        if result['has_more']:
            self.cursor = result['next_cursor']
        else:
            self.cursor = False

        return result['results']

