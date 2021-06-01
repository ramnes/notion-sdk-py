## pagination support for the Notion API

CONTENT_PAGE_SIZE = 100

################################################################################
# base class to handle pagination support
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

################################################################################
# handle database queries
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


