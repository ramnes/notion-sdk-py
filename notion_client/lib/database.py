"""Database object and property classes."""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Type

from .custom_enums import NumberPropertyFormat, RollupFunctionType
from .datatypes import APIObject, MultiselectOption, Property, RichText, SelectOption


@dataclass
class Database(APIObject):
    title: List[RichText]
    properties: Dict[str, Property]

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "Database":
        """Create a Database from its JSON equaivalent, retrieved from Notion API."""
        return Database(
            id=d["id"],
            object="database",
            created_time=datetime.strptime(d["created_time"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            last_edited_time=datetime.strptime(
                d["last_edited_time"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            title=[RichText.from_json(title) for title in d["title"]],
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

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "RollupProperty":
        """Create a RollupProperty from its JSON equaivalent."""
        rollup_type = d.pop("rollup_property_id")
        rollup_property: RollupProperty = super(cls, RollupProperty).from_json(d)
        rollup_property.format = RollupFunctionType(rollup_type)
        return rollup_property


@dataclass
class NumberProperty(Property):
    format: NumberPropertyFormat

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "NumberProperty":
        """Create a NumberProperty from its JSON equaivalent."""
        number_format = d.pop("format")
        number_property: NumberProperty = super(cls, NumberProperty).from_json(d)
        number_property.format = NumberPropertyFormat(number_format)
        return number_property


@dataclass
class SelectProperty(Property):
    options: List[SelectOption]

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "SelectProperty":
        """Create a SelectProperty from its JSON equaivalent."""
        select_configuration = d.pop("select")
        select_property: SelectProperty = super(cls, SelectProperty).from_json(d)
        select_property.options = [
            SelectOption(**x) for x in select_configuration["options"]
        ]
        return select_property


@dataclass
class MultiselectProperty(Property):
    options: List[MultiselectOption]

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "MultiselectProperty":
        """Create a MultiSelectProperty from its JSON equaivalent."""
        select_configuration = d.pop("multi_select")
        multiselect_property: MultiselectProperty = super(
            cls, MultiselectProperty
        ).from_json(d)
        multiselect_property.options = [
            MultiselectOption(**x) for x in select_configuration["options"]
        ]
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


def database_property_from_json(d: Dict[str, Any]) -> Property:
    """Make database property JSON Pythonic."""
    property_type = d["type"]
    property_type_to_class: Dict[str, Type[Property]] = {
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
