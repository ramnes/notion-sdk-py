from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from .custom_enums import BasicColor, BlockType, RollupValueTypes, UserType
from .database import Property
from .datatypes import (
    APIObject,
    Bot,
    FileReference,
    PageParent,
    PageReference,
    Person,
    RichText,
)


@dataclass
class Block(APIObject):
    type: BlockType
    has_children: bool
    text: List[RichText]
    children: Optional[List["Block"]]
    checked: Optional[bool]  # for BlockType.Todo
    title: Optional[str]  # for BlockType.ChildPage

    @classmethod
    def from_json(cls, d: Dict[str, object]) -> "Block":
        children = d.get("children")
        if not children:
            children = []
        return Block(
            id=d["id"],
            object="block",
            created_time=datetime.strptime(d["created_time"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            last_edited_time=datetime.strptime(
                d["last_edited_time"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            type=BlockType(d["type"]),
            has_children=d["has_children"],
            text=[RichText.from_json(r) for r in d["text"]],
            children=[Block.from_json(b) for b in children],
            checked=d.get("checked"),
            title=d.get("title"),
        )


@dataclass
class Page(APIObject):
    parent: PageParent
    archived: bool
    properties: Dict[str, "PropertyValue"]

    @classmethod
    def from_json(cls, d: Dict[str, object]) -> "Page":
        return Page(
            id=d["id"],
            object="page",
            archived=d["archived"],
            created_time=datetime.strptime(d["created_time"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            last_edited_time=datetime.strptime(
                d["last_edited_time"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            parent=PageParent.from_json(d["parent"]),
            properties=dict(
                [(k, property_value_from_json(v)) for (k, v) in d["properties"].items()]
            ),
        )


@dataclass
class User(APIObject):
    type: UserType
    name: str
    avatar_url: str
    person: Person
    bot: Bot

    @classmethod
    def from_json(cls, d: Dict[str, str]) -> "User":
        user_type = UserType(d.get("type"))
        return User(
            id=d["id"],
            object="user",
            created_time=datetime.strptime(d["created_time"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            last_edited_time=datetime.strptime(
                d["last_edited_time"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            type=user_type,
            name=d.get("name"),
            avatar_url=d.get("avatar_url"),
            person=Person(email=d["email"]) if user_type == UserType.person else None,
            bot=Bot() if user_type == UserType.bot else None,
        )


def property_value_from_json(d: Dict[str, object]) -> "PropertyValue":
    property_type = d["type"]
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
        "last_edited_by": LastEditedByPropertyValue,
    }
    return property_type_to_class[property_type].from_json(d)


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

    @classmethod
    def from_json(cls, d) -> "FormulaPropertyValue":

        date = None
        relations = None
        if d.get("date"):
            date = d.pop("date")

        if d.get("relation"):
            relations = d.pop("relations")

        formula: FormulaPropertyValue = super(FormulaPropertyValue, cls).from_json(d)

        if relations:
            formula.relation = [PageReference.from_json(x) for x in relations]

        if date:
            formula.date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")

        return formula


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

    @classmethod
    def from_json(cls, d) -> "RollupPropertyValue":

        date = None
        relations = None
        if d.get("date"):
            date = d.pop("date")
        if d.get("relation"):
            relations = d.pop("relations")

        rollup: RollupPropertyValue = super(FormulaPropertyValue, cls).from_json(d)

        if relations:
            rollup.relation = [PageReference.from_json(x) for x in relations]
        if date:
            rollup.date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")

        return rollup


@dataclass
class NumberPropertyValue(PropertyValue):
    number: float


@dataclass
class SelectPropertyValue(PropertyValue):
    name: str

    # explicit override of the id in Property. See
    # https://developers.notion.com/reference/page#select-property-values
    id: str
    color: BasicColor


@dataclass
class MultiselectPropertyValue(SelectPropertyValue):
    pass


@dataclass
class TitlePropertyValue(PropertyValue):
    title: List[RichText]

    @classmethod
    def from_json(cls, d) -> "TitlePropertyValue":
        titles = None
        if d.get("title"):
            titles = d.pop("title")

        title_property: TitlePropertyValue = super(TitlePropertyValue, cls).from_json(d)

        if titles:
            title_property.title = [RichText.from_json(x) for x in titles]
        return title_property


@dataclass
class RichTextPropertyValue(PropertyValue):
    rich_text: List[RichText]

    @classmethod
    def from_json(cls, d) -> "RichTextPropertyValue":
        rich_text = None
        if d.get("rich_text"):
            rich_text = d.pop("rich_text")

        rich_text_property: RichTextPropertyValue = super(
            RichTextPropertyValue, cls
        ).from_json(d)

        if rich_text:
            rich_text_property.rich_text = [RichText.from_json(x) for x in rich_text]
        return rich_text_property


@dataclass
class DatePropertyValue(PropertyValue):
    start: datetime
    end: datetime

    @classmethod
    def from_json(cls, d) -> "DatePropertyValue":
        start = d.pop("start")
        end = None
        if d.get("end"):
            end = d.pop("end")

        date: DatePropertyValue = super(DatePropertyValue, cls).from_json(d)

        if start:
            date.start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.%fZ")
        if end:
            date.end = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S.%fZ")
        return date


@dataclass
class PeoplePropertyValue(PropertyValue):
    people: List[User]

    @classmethod
    def from_json(cls, d) -> "PeoplePropertyValue":
        people = d.pop("people")
        people_property: PeoplePropertyValue = super(
            PeoplePropertyValue, cls
        ).from_json(d)

        people_property.people = [User.from_json(p) for p in people]
        return people_property


@dataclass
class FilePropertyValue(PropertyValue):
    files: List[FileReference]

    @classmethod
    def from_json(cls, d) -> "FilePropertyValue":
        files = d.pop("files")
        file_property: FilePropertyValue = super(FilePropertyValue, cls).from_json(d)

        file_property.files = [FileReference(name=f["name"]) for f in files]
        return file_property


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

    @classmethod
    def from_json(cls, d) -> "CreatedTimePropertyValue":
        time = d.pop("created_time")
        created_time_property: CreatedTimePropertyValue = super(
            CreatedTimePropertyValue, cls
        ).from_json(d)
        created_time_property.created_time = datetime.strptime(
            time, "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        return created_time_property


@dataclass
class CreatedByPropertyValue(PropertyValue):
    created_by: User

    @classmethod
    def from_json(cls, d) -> "CreatedByPropertyValue":
        created_by = d.pop("created_by")
        created_by_property: CreatedTimePropertyValue = super(
            CreatedByPropertyValue, cls
        ).from_json(d)
        created_by_property.created_by = User.from_json(created_by)
        return created_by_property


@dataclass
class LastEditedTimePropertyValue(PropertyValue):
    last_edited_time: datetime

    @classmethod
    def from_json(cls, d) -> "LastEditedByPropertyValue":
        time = d.pop("last_edited_time")
        last_edited_time_property: LastEditedTimePropertyValue = super(
            LastEditedTimePropertyValue, cls
        ).from_json(d)
        last_edited_time_property.last_edited_time = datetime.strptime(
            time, "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        return last_edited_time_property


@dataclass
class LastEditedByPropertyValue(PropertyValue):
    last_edited_by: User

    @classmethod
    def from_json(cls, d) -> "LastEditedByPropertyValue":
        last_edited_by = d.pop("last_edited_by")
        last_edited_by_property: LastEditedByPropertyValue = super(
            LastEditedByPropertyValue, cls
        ).from_json(d)
        last_edited_by_property.created_by = User.from_json(last_edited_by)
        return last_edited_by_property
