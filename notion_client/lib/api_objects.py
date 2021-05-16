from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from custom_enums import UserType
from datatypes import Bot, PageParent, Person, RichText
from property import Property, database_property_from_json
from property_values import PropertyValue, page_property_from_json


@dataclass
class APIObject:
    id: str
    object: str
    created_time: datetime
    last_edited_time: datetime


@dataclass
class User(APIObject):
    type: UserType
    name: str
    avatar_url: str
    person: Person
    bot: Bot

    @classmethod
    def from_json(cls, d: Dict[str, str]):
        user_type = UserType(d.get("type"))
        return User(
            id=d["id"],
            object="user",
            type=user_type,
            name=d.get("name"),
            avatar_url=d.get("avatar_url"),
            person=Person(email=d["email"]) if user_type == UserType.person else None,
            bot=Bot() if user_type == UserType.bot else None,
        )


@dataclass
class Database(APIObject):
    title: List[RichText]
    properties: Dict[str, Property]

    @classmethod
    def from_json(cls, d: Dict[str, object]):
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
class PageObject(APIObject):
    parent: PageParent
    archived: bool
    properties: Dict[str, PropertyValue]

    @classmethod
    def from_json(cls, d: Dict[str, object]):
        return PageObject(
            id=d["id"],
            object="page",
            archived=d.get("archived"),
            created_time=datetime.strptime(d["created_time"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            last_edited_time=datetime.strptime(
                d["last_edited_time"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            parent=PageParent.from_json(d.get("parent")),
            properties=dict(
                [(k, page_property_from_json(v)) for (k, v) in d["properties"].items()]
            ),
        )
