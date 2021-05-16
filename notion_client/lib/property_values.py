from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from api_objects import User
from custom_enums import (
    BasicColor,
    RollupValueTypes
)
from datatypes import (
    FileReference,
    PageReference,
    RichText,
)
from property import Property


@dataclass
class PropertyValue(Property):
    pass

@dataclass
class RollupPropertyElement(PropertyValue):
    id = None

@dataclass
class FormulaPropertyValue(PropertyValue):
    type: str
    string: str
    number: float
    boolean: bool
    date: datetime
    relation: List[PageReference]


@dataclass
class RelationPropertyValue(PropertyValue):
    database_id: str
    synced_property_name: str
    synced_property_id: str


@dataclass
class RollupPropertyValue(PropertyValue):
    type: RollupValueTypes
    number: float
    date: datetime
    array: List[RollupPropertyElement]


@dataclass
class NumberPropertyValue(PropertyValue):
    number: float


@dataclass
class SelectPropertyValue(PropertyValue):
    name: str
    id: str # explicit override of the id in Property. See https://developers.notion.com/reference/page#select-property-values
    color: BasicColor


@dataclass
class MultiselectPropertyValue(SelectPropertyValue):
    pass


@dataclass
class TitlePropertyValue(PropertyValue):
    title: List[RichText]


@dataclass
class RichTextPropertyValue(PropertyValue):
    rich_text: List[RichText]


@dataclass
class DatePropertyValue(PropertyValue):
    start: datetime
    end: datetime


@dataclass
class PeoplePropertyValue(PropertyValue):
    people: List[User]


@dataclass
class FilePropertyValue(PropertyValue):
    files: List[FileReference]


@dataclass
class CheckboxPropertyValue(PropertyValue):
    checkbox: bool


@dataclass
class UrlPropertyValue(PropertyValue):
    url: str


@dataclass
class EmailPropertyValue(PropertyValue):
    email: str


@dataclass
class PhoneNumberPropertyValue(PropertyValue):
    phone_number: str


@dataclass
class CreatedTimePropertyValue(PropertyValue):
    created_time: datetime


@dataclass
class CreatedByPropertyValue(PropertyValue):
    created_by: User


@dataclass
class LastEditedTimePropertyValue(PropertyValue):
    last_edited_time: datetime


@dataclass
class LastEditedByPropertyValue(PropertyValue):
    last_edited_by: User


def page_property_from_dict(d: Dict[str, object]) -> PropertyValue:
    property_type = d['type']
    property_type_to_class = {
        "title": TitlePropertyValue,
        "rich_text": RichTextPropertyValue,
        "number": NumberPropertyValue,
        "select": SelectPropertyValue,
        "multi_select": MultiselectPropertyValue,
        "date": DatePropertyValue,
        "people": PeoplePropertyValue,
        "file": FilePropertyValue,
        "checkbox": CheckboxPropertyValue,
        "url": UrlPropertyValue,
        "email": EmailPropertyValue,
        "phone_number": PhoneNumberPropertyValue,
        "formula": FormulaPropertyValue,
        "relation": RelationPropertyValue,
        "rollup": RollupPropertyValue,
        "created_time": CreatedTimePropertyValue,
        "created_by": CreatedByPropertyValue,
        "last_edited_time": LastEditedTimePropertyValue,
        "last_edited_by": LastEditedByPropertyValue
    }
    return property_type_to_class[property_type].from_dict(d)
