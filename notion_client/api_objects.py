from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List


class RichTextType(Enum):
    text = "text"
    mention = "mention"
    equation = "equation"


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


@dataclass
class Annotations:
    bold: bool
    italic: bool
    strikethrough: bool
    underline: bool
    code: bool
    color: Color


@dataclass
class RichText:
    plain_text: str
    href: str
    annotations: Annotations
    type: RichTextType


@dataclass
class DatabaseObject:
    id: str
    created_time: datetime
    last_edited_time: datetime
    title: List[RichText]
    object: str = "database"
