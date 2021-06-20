"""Enums for Notion API fields that have a finite set of possible values."""


from enum import Enum


class BasicColor(str, Enum):
    default = "default"
    gray = "gray"
    brown = "brown"
    orange = "orange"
    yellow = "yellow"
    green = "green"
    blue = "blue"
    purple = "purple"
    pink = "pink"
    red = "red"


class BlockType(str, Enum):
    paragraph = "paragraph"
    heading_one = "heading_1"
    heading_two = "heading_2"
    heading_three = "heading_3"
    bulleted_list_item = "bulleted_list_item"
    numbered_list_item = "numbered_list_item"
    to_do = "to_do"
    toggle = "toggle"
    child_page = "child_page"
    unsupported = "unsupported"


class Color(str, Enum):
    default = "default"
    gray = "gray"
    brown = "brown"
    orange = "orange"
    yellow = "yellow"
    green = "green"
    blue = "blue"
    purple = "purple"
    pink = "pink"
    red = "red"
    gray_background = "gray_background"
    brown_background = "brown_background"
    orange_background = "orange_background"
    yellow_background = "yellow_background"
    green_background = "green_background"
    blue_background = "blue_background"
    purple_background = "purple_background"
    pink_background = "pink_background"
    red_background = "red_background"


class NumberPropertyFormat(str, Enum):
    number = "number"
    number_with_commas = "number_with_commas"
    percent = "percent"
    dollar = "dollar"
    euro = "euro"
    pound = "pound"
    yen = "yen"
    ruble = "ruble"
    rupee = "rupee"
    won = "won"
    yuan = "yuan"


class ParentType(str, Enum):
    page = "page_id"
    database = "database_id"
    workspace = "workspace"


class PropertyType(str, Enum):
    _title = "title"
    rich_text = "rich_text"
    number = "number"
    select = "select"
    multi_select = "multi_select"
    date = "date"
    people = "people"
    file = "file"
    checkbox = "checkbox"
    url = "url"
    email = "email"
    phone_number = "phone_number"
    formula = "formula"
    relation = "relation"
    rollup = "rollup"
    created_time = "created_time"
    created_by = "created_by"
    last_edited_time = "last_edited_time"
    last_edited_by = "last_edited_by"


class RichTextType(str, Enum):
    text = "text"
    mention = "mention"
    equation = "equation"


class RollupFunctionType(str, Enum):
    count_all = "count_all"
    count_values = "count_values"
    count_unique_values = "count_unique_values"
    count_empty = "count_empty"
    count_not_empty = "count_not_empty"
    percent_empty = "percent_empty"
    percent_not_empty = "percent_not_empty"
    sum = "sum"
    average = "average"
    median = "median"
    min = "min"
    max = "max"
    range = "range"


class RollupValueTypes(str, Enum):
    number = "number"
    date = "date"
    array = "array"


class UserType(str, Enum):
    person = "person"
    bot = "bot"
