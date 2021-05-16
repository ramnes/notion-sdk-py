from dataclasses import dataclass
from typing import Dict, List

from custom_enums import NumberPropertyFormat, PropertyType, RollupFunctionType
from datatypes import MultiselectOption, SelectOption


@dataclass
class Property:
    id: str
    type: PropertyType

    @classmethod
    def from_dict(cls, d: Dict[str, str]):
        return Property(id=d["id"], type=PropertyType(d["type"]))


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


@dataclass
class SelectProperty(Property):
    options: List[SelectOption]


@dataclass
class MultiselectProperty(Property):
    options: List[MultiselectOption]


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


def database_property_from_dict(d: Dict[str, object]) -> Property:
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
    return property_type_to_class[property_type].from_dict(d)
