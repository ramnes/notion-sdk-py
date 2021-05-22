from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Union

from .custom_enums import NumberPropertyFormat, RollupFunctionType
from .datatypes import APIObject, MultiselectOption, Property, RichText, SelectOption


@dataclass
class Database(APIObject):
    title: List[RichText]
    properties: Dict[str, Property]

    @classmethod
    def from_json(cls, d: Dict[str, object]) -> "Database":
        return Database(
            id=d["id"],
            object="database",
            created_time=datetime.strptime(d["created_time"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            last_edited_time=datetime.strptime(
                d["last_edited_time"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            title=RichText.from_json(d["title"][0]),
            properties=dict(
                [
                    (k, database_property_from_json(v))
                    for (k, v) in d["properties"].items()
                ]
            ),
        )


@dataclass
class FormulaProperty(Property):
    expression: str


@dataclass
class RelationProperty(Property):
    database_id: str
    synced_property_name: str
    synced_property_id: str


@dataclass
class RollupProperty(Property):
    relation_property_name: str
    relation_property_id: str
    rollup_property_name: str
    rollup_property_id: RollupFunctionType


@dataclass
class NumberProperty(Property):
    format: NumberPropertyFormat

    @classmethod
    def from_json(cls, d: Dict[str, Union[str, List[str]]]) -> "NumberProperty":
        number_property: NumberProperty = super(NumberProperty).from_json(
            NumberProperty, d
        )
        number_property.options = [NumberPropertyFormat(x) for x in d["options"]]
        return number_property


@dataclass
class SelectProperty(Property):
    options: List[SelectOption]

    @classmethod
    def from_json(cls, d: Dict[str, Union[str, List[str]]]) -> "SelectProperty":
        select_property: SelectProperty = super(SelectProperty).from_json(
            SelectProperty, d
        )
        select_property.options = [SelectOption(x) for x in d["options"]]
        return select_property


@dataclass
class MultiselectProperty(Property):
    options: List[MultiselectOption]

    @classmethod
    def from_json(cls, d: Dict[str, Union[str, List[str]]]) -> "MultiselectProperty":
        multiselect_property: MultiselectProperty = super(
            MultiselectProperty
        ).from_json(MultiselectProperty, d)
        multiselect_property.options = [MultiselectOption(x) for x in d["options"]]
        return multiselect_property


@dataclass
class TitleProperty(Property):
    pass


@dataclass
class RichTextProperty(Property):
    pass


@dataclass
class DateProperty(Property):
    pass


@dataclass
class PeopleProperty(Property):
    pass


@dataclass
class FileProperty(Property):
    pass


@dataclass
class CheckboxProperty(Property):
    pass


@dataclass
class UrlProperty(Property):
    pass


@dataclass
class EmailProperty(Property):
    pass


@dataclass
class PhoneNumberProperty(Property):
    pass


@dataclass
class CreatedTimeProperty(Property):
    pass


@dataclass
class CreatedByProperty(Property):
    pass


@dataclass
class LastEditedTimeProperty(Property):
    pass


@dataclass
class LastEditedByProperty(Property):
    pass


def database_property_from_json(d: Dict[str, object]) -> Property:
    property_type = d["type"]
    property_type_to_class = {
        "title": TitleProperty,
        "rich_text": RichTextProperty,
        "number": NumberProperty,
        "select": SelectProperty,
        "multi_select": MultiselectProperty,
        "date": DateProperty,
        "people": PeopleProperty,
        "file": FileProperty,
        "checkbox": CheckboxProperty,
        "url": UrlProperty,
        "email": EmailProperty,
        "phone_number": PhoneNumberProperty,
        "formula": FormulaProperty,
        "relation": RelationProperty,
        "rollup": RollupProperty,
        "created_time": CreatedTimeProperty,
        "created_by": CreatedByProperty,
        "last_edited_time": LastEditedTimeProperty,
        "last_edited_by": LastEditedByProperty,
    }
    return property_type_to_class[property_type].from_json(d)
