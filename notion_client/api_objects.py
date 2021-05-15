from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class RichTextType(Enum):
    text = "text"
    mention = "mention"
    equation = "equation"

class ParentType(Enum):
    page = "page_id"
    database = "database_id"
    workspace = "workspace"

class BasicColor(Enum):
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


class Color(Enum):
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


class RollupFunctionType(Enum):
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


class DatabasePropertyType(Enum):
    title = "title"
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


class NumberPropertyFormat(Enum):
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


@dataclass
class Annotations:
    bold: bool
    italic: bool
    strikethrough: bool
    underline: bool
    code: bool
    color: Color

    @classmethod
    def from_dict(cls, d: Dict[str, object]):
        print("annotation", d)
        return Annotations(
            bold=d["bold"],
            italic=d["italic"],
            strikethrough=d["strikethrough"],
            underline=d["underline"],
            code=d["code"],
            color=Color(d["color"])
        )


@dataclass
class RichText:
    plain_text: str
    href: str
    annotations: Annotations
    type: RichTextType

    @classmethod
    def from_dict(cls, d: Dict[str, object]):
        return RichText(
            plain_text=d.get('plain_text'),
            href=d.get('href'),
            annotations=Annotations.from_dict(d.get("annotations")),
            type=RichTextType(d["type"])
        )


@dataclass
class SelectOption:
    name: str
    id: str
    color: BasicColor


@dataclass
class MultiselectOption(SelectOption):
    pass


@dataclass
class DatabaseProperty:
    id: str
    type: DatabasePropertyType

    @classmethod
    def from_dict(cls, d: Dict[str, str]):
        return DatabaseProperty(
            id=d["id"],
            type=DatabasePropertyType(d["type"])
        )


@dataclass
class FormulaDatabaseProperty(DatabaseProperty):
    expression: str


@dataclass
class RelationDatabaseProperty(DatabaseProperty):
    database_id: str
    synced_property_name: str
    synced_property_id: str


@dataclass
class RollupDatabaseProperty(DatabaseProperty):
    relation_property_name: str
    relation_property_id: str
    rollup_property_name: str
    rollup_property_id: RollupFunctionType


@dataclass
class NumberDatabaseProperty(DatabaseProperty):
    format: NumberPropertyFormat


@dataclass
class SelectDatabaseProperty(DatabaseProperty):
    options: List[SelectOption]


@dataclass
class MultiselectDatabaseProperty(DatabaseProperty):
    options: List[MultiselectOption]


@dataclass
class TitleDatabaseProperty(DatabaseProperty):
    pass


@dataclass
class RichTextDatabaseProperty(DatabaseProperty):
    pass


@dataclass
class DateDatabaseProperty(DatabaseProperty):
    pass


@dataclass
class PeopleDatabaseProperty(DatabaseProperty):
    pass


@dataclass
class FileDatabaseProperty(DatabaseProperty):
    pass


@dataclass
class CheckboxDatabaseProperty(DatabaseProperty):
    pass


@dataclass
class UrlDatabaseProperty(DatabaseProperty):
    pass


@dataclass
class EmailDatabaseProperty(DatabaseProperty):
    pass


@dataclass
class PhoneNumberDatabaseProperty(DatabaseProperty):
    pass


@dataclass
class CreatedTimeDatabaseProperty(DatabaseProperty):
    pass


@dataclass
class CreatedByDatabaseProperty(DatabaseProperty):
    pass


@dataclass
class LastEditedTimeDatabaseProperty(DatabaseProperty):
    pass


@dataclass
class LastEditedByDatabaseProperty(DatabaseProperty):
    pass


def database_property_from_dict(d: Dict[str, object]) -> DatabaseProperty:
    property_type = d['type']
    property_type_to_class = {
        "title": TitleDatabaseProperty,
        "rich_text": RichTextDatabaseProperty,
        "number": NumberDatabaseProperty,
        "select": SelectDatabaseProperty,
        "multi_select": MultiselectDatabaseProperty,
        "date": DateDatabaseProperty,
        "people": PeopleDatabaseProperty,
        "file": FileDatabaseProperty,
        "checkbox": CheckboxDatabaseProperty,
        "url": UrlDatabaseProperty,
        "email": EmailDatabaseProperty,
        "phone_number": PhoneNumberDatabaseProperty,
        "formula": FormulaDatabaseProperty,
        "relation": RelationDatabaseProperty,
        "rollup": RollupDatabaseProperty,
        "created_time": CreatedTimeDatabaseProperty,
        "created_by": CreatedByDatabaseProperty,
        "last_edited_time": LastEditedTimeDatabaseProperty,
        "last_edited_by": LastEditedByDatabaseProperty
    }
    return property_type_to_class[property_type].from_dict(d)


def page_property_from_dict(d: Dict[str, object]) -> DatabaseProperty:
    property_type = d['type']
    property_type_to_class = {
        "title": TitleDatabaseProperty,
        "rich_text": RichTextDatabaseProperty,
        "number": NumberDatabaseProperty,
        "select": SelectDatabaseProperty,
        "multi_select": MultiselectDatabaseProperty,
        "date": DateDatabaseProperty,
        "people": PeopleDatabaseProperty,
        "file": FileDatabaseProperty,
        "checkbox": CheckboxDatabaseProperty,
        "url": UrlDatabaseProperty,
        "email": EmailDatabaseProperty,
        "phone_number": PhoneNumberDatabaseProperty,
        "formula": FormulaDatabaseProperty,
        "relation": RelationDatabaseProperty,
        "rollup": RollupDatabaseProperty,
        "created_time": CreatedTimeDatabaseProperty,
        "created_by": CreatedByDatabaseProperty,
        "last_edited_time": LastEditedTimeDatabaseProperty,
        "last_edited_by": LastEditedByDatabaseProperty
    }
    return property_type_to_class[property_type].from_dict(d)

@dataclass
class APIObject:
    id: str
    object: str
    created_time: datetime
    last_edited_time: datetime


@dataclass
class DatabaseObject(APIObject):
    title: List[RichText]
    properties: Dict[str, DatabaseProperty]

    @classmethod
    def from_dict(cls, d: Dict[str, object]):
        return DatabaseObject(
            id=d['id'],
            object="database",
            created_time=datetime.strptime(d['created_time'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            last_edited_time=datetime.strptime(d['last_edited_time'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            title=RichText.from_dict(d['title'][0]),
            properties=dict([
                (k, database_property_from_dict(v)) for (k, v) in d["properties"].items()
            ])
        )

@dataclass
class PageParent:
    type: ParentType
    id: str

    @classmethod
    def from_dict(cls, d: Dict[str, object]):
        type = ParentType(d['type'])
        return PageParent(
            id=d.get("database_id" if type == ParentType.database else "page_id"),
            type=type,
        )

@dataclass
class PageObject(APIObject):
    parent: PageParent
    archived: bool
    properties: Dict[str, DatabaseProperty]


    @classmethod
    def from_dict(cls, d: Dict[str, object]):
        return PageObject(
            id=d['id'],
            object="page",
            archived=d['archived'],
            created_time=datetime.strptime(d['created_time'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            last_edited_time=datetime.strptime(d['last_edited_time'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            parent=PageParent.from_dict(d['parent']),
            properties=dict([
                (k, page_property_from_dict(v)) for (k, v) in d["properties"].items()
            ])
        )
