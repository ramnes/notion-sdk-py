from dataclasses import dataclass
from typing import Dict, List

from custom_enums import (
    DatabasePropertyType,
    NumberPropertyFormat,
    RollupFunctionType
)
from datatypes import (
    MultiselectOption,
    SelectOption
)


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
