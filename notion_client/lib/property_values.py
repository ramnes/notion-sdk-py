from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from api_objects import User
from custom_enums import BasicColor, RollupValueTypes
from datatypes import FileReference, PageReference, RichText
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

    @classmethod
    def from_json(cls, d):

        date = None
        relations = None
        if d.get("date"):
            date = d.pop("date")

        if d.get("relation"):
            relations = d.pop("relations")

        formula = super(FormulaPropertyValue).from_json(FormulaPropertyValue, d)

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
    def from_json(cls, d):

        date = None
        relations = None
        if d.get("date"):
            date = d.pop("date")
        if d.get("relation"):
            relations = d.pop("relations")

        rollup = super(FormulaPropertyValue).from_json(FormulaPropertyValue, d)

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
    id: str  # explicit override of the id in Property. See https://developers.notion.com/reference/page#select-property-values
    color: BasicColor


@dataclass
class MultiselectPropertyValue(SelectPropertyValue):
    pass


@dataclass
class TitlePropertyValue(PropertyValue):
    title: List[RichText]

    @classmethod
    def from_json(cls, d):
        titles = None
        if d.get("title"):
            titles = d.pop("title")

        title_property = super(TitlePropertyValue).from_json(TitlePropertyValue, d)

        if titles:
            title_property.title = [RichText.from_json(x) for x in titles]
        return title_property


@dataclass
class RichTextPropertyValue(PropertyValue):
    rich_text: List[RichText]

    @classmethod
    def from_json(cls, d):
        rich_text = None
        if d.get("rich_text"):
            rich_text = d.pop("rich_text")

        rich_text_property = super(RichTextPropertyValue).from_json(
            RichTextPropertyValue, d
        )

        if rich_text:
            rich_text_property.rich_text = [RichText.from_json(x) for x in rich_text]

        return rich_text_property


@dataclass
class DatePropertyValue(PropertyValue):
    start: datetime
    end: datetime

    @classmethod
    def from_json(cls, d):
        start = d.pop("start")
        end = None
        if d.get("end"):
            end = d.pop("end")

        date = super(DatePropertyValue).from_json(DatePropertyValue, d)

        if start:
            date.start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.%fZ")
        if end:
            date.end = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S.%fZ")
        return date


@dataclass
class PeoplePropertyValue(PropertyValue):
    people: List[User]

    @classmethod
    def from_json(cls, d):
        people = d.pop("people")
        people_property = super(PeoplePropertyValue).from_json(PeoplePropertyValue, d)

        people_property.people = [User(p) for p in people]
        return people_property


@dataclass
class FilePropertyValue(PropertyValue):
    files: List[FileReference]

    @classmethod
    def from_json(cls, d):
        files = d.pop("files")
        file_property = super(FilePropertyValue).from_json(FilePropertyValue, d)

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
    def from_json(cls, d):
        time = d.pop("created_time")
        created_time_property = super(CreatedTimePropertyValue).from_json(
            CreatedTimePropertyValue, d
        )
        created_time_property.created_time = datetime.strptime(
            time, "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        return created_time_property


@dataclass
class CreatedByPropertyValue(PropertyValue):
    created_by: User

    @classmethod
    def from_json(cls, d):
        created_by = d.pop("created_by")
        created_by_property = super(CreatedByPropertyValue).from_json(
            CreatedByPropertyValue, d
        )
        created_by_property.created_by = User.from_json(created_by)
        return created_by_property


@dataclass
class LastEditedTimePropertyValue(PropertyValue):
    last_edited_time: datetime

    @classmethod
    def from_json(cls, d):
        time = d.pop("last_edited_time")
        last_edited_time_property = super(LastEditedTimePropertyValue).from_json(
            LastEditedTimePropertyValue, d
        )
        last_edited_time_property.last_edited_time = datetime.strptime(
            time, "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        return last_edited_time_property


@dataclass
class LastEditedByPropertyValue(PropertyValue):
    last_edited_by: User

    @classmethod
    def from_json(cls, d):
        last_edited_by = d.pop("last_edited_by")
        last_edited_by_property = super(LastEditedByPropertyValue).from_json(
            LastEditedByPropertyValue, d
        )
        last_edited_by_property.created_by = User.from_json(last_edited_by)
        return last_edited_by_property


def page_property_from_json(d: Dict[str, object]) -> PropertyValue:
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
