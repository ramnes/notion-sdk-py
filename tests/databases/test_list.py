from notion_client import Client
from notion_client.errors import APIErrorCode
from tests.conftest import PROPER_AUTH


def test_list():
    wrong_client = Client({"auth": "foo"})
    try:
        data = wrong_client.databases.list()
    except Exception as error:
        assert error.code == APIErrorCode.Unauthorized.value
    proper_client = Client({"auth": PROPER_AUTH})
    data = proper_client.databases.list()
    assert data == {"foo": "bar"}
