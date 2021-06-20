import datetime

from notion_client.lib import Database, SelectOption


def test_database(database_json):

    result = Database.from_json(database_json)

    assert result.object == "database"
    assert result.created_time == datetime.datetime(2021, 5, 28, 9, 53, 15, 949000)
    assert result.last_edited_time == datetime.datetime(2021, 5, 29, 7, 11)

    assert len(result.title) == 1
    title = result.title[0]
    assert title.type == "text"
    assert title.plain_text == "Test database"
    assert title.href is None

    annotations = title.annotations
    assert annotations.bold
    assert annotations.underline

    assert not annotations.italic
    assert not annotations.strikethrough
    assert not annotations.code
    assert annotations.color == "yellow"

    assert len(result.properties) == 4
    properties = result.properties
    assert properties["Property"].type == "formula"
    assert properties["Property"].expression == 'prop("Status") == "Complete"'

    assert properties["Website"].type == "rich_text"
    assert properties["Status"].type == "select"
    assert len(properties["Status"].options) == 4
    options = properties["Status"].options
    for o in options:
        assert type(o) == SelectOption
