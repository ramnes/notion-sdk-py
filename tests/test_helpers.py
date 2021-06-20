import pytest

from notion_client.helpers import get_id, get_url, pick


def test_pick():
    my_dict = {"Product": "Notion", "API": 2021, "python-sdk": "ramnes"}
    assert pick(my_dict, "Product") == {"Product": "Notion"}
    assert pick(my_dict, "API", "python-sdk") == {
        "API": 2021,
        "python-sdk": "ramnes",
    }


def test_get_id():
    page_url = "https://notion.so/aahnik/Aahnik-Daw-621cc4c1ad324159bcea215ce18e03a8"
    page_id = "621cc4c1-ad32-4159-bcea-215ce18e03a8"
    db_url = "https://notion.so/aahnik/99572135464649bd95a14ff08f79c7a5?\
            v=f41969f937614159857f6a5725990649"
    db_id = "99572135-4646-49bd-95a1-4ff08f79c7a5"
    assert get_id(page_url) == page_id
    assert get_id(db_url) == db_id
    with pytest.raises(ValueError):
        get_id("https://example.com")
        get_id("https://notion.so/123")
        get_id("https://notion.so/99572135464649b-d95a14ff08f79c7a5")


def test_get_url():
    dashed_id = "540f8e2b-7991-4654-ba10-3c5d8a03e10e"
    obj_id = "540f8e2b79914654ba103c5d8a03e10e"
    url = "https://notion.so/540f8e2b79914654ba103c5d8a03e10e"
    assert get_url(dashed_id) == url
    assert get_url(obj_id) == url
    with pytest.raises(ValueError):
        get_url("540f8e2b799-14654ba103c5d8a03-e10e")
        get_url("123abc")
