from dataclasses import dataclass
from typing import Dict

from custom_enums import (
    BasicColor,
    Color,
    RichTextType
)

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
