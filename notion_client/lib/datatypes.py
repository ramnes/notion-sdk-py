from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Union

from .custom_enums import BasicColor, Color, ParentType, PropertyType, RichTextType


@dataclass
class Annotations:
    bold: bool
    italic: bool
    strikethrough: bool
    underline: bool
    code: bool
    color: Color

    @classmethod
    def from_json(cls, d: Dict[str, Union[bool, Color]]) -> "Annotations":
        return Annotations(
            bold=d["bold"],
            italic=d["italic"],
            strikethrough=d["strikethrough"],
            underline=d["underline"],
            code=d["code"],
            color=Color(d["color"]),
        )


@dataclass
class Property:
    id: str
    type: PropertyType

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "Property":

        required_fields = cls.__dataclass_fields__

        # Try converting all json datatypes to their dataclass type (e.g Enum).
        # Property subclasses with more complicated data types will
        # have to override `from_json`
        for k in required_fields.keys():
            if d.get(k) is not None:
                d[k] = required_fields[k].type(d.get(k))

        required_data = dict([(k, d.get(k)) for k in required_fields.keys()])
        return cls(**required_data)


@dataclass
class APIObject:
    id: str
    object: str
    created_time: datetime
    last_edited_time: datetime


@dataclass
class Bot:
    pass


@dataclass
class Person:
    email: str


@dataclass
class PageReference:
    id: str


@dataclass
class PageParent:
    type: ParentType
    id: str

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "PageParent":
        type = ParentType(d["type"])
        return PageParent(
            id=d.get("database_id" if type == ParentType.database else "page_id"),
            type=type,
        )


@dataclass
class FileReference:
    name: str


@dataclass
class RichText:
    plain_text: str
    href: str
    annotations: Annotations
    type: RichTextType

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "RichText":
        return RichText(
            plain_text=d.get("plain_text"),
            href=d.get("href"),
            annotations=Annotations.from_json(d.get("annotations")),
            type=RichTextType(d["type"]),
        )


@dataclass
class SelectOption:
    name: str
    id: str
    color: BasicColor


@dataclass
class MultiselectOption(SelectOption):
    pass
