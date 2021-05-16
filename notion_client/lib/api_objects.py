from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from datatypes import PageParent, RichText
from property import Property, database_property_from_dict
from property_values import PropertyValue, page_property_from_dict


@dataclass
class APIObject:
    id: str
    object: str
    created_time: datetime
    last_edited_time: datetime


@dataclass
class User(APIObject):
    pass


@dataclass
class Database(APIObject):
    title: List[RichText]
    properties: Dict[str, Property]

    @classmethod
    def from_dict(cls, d: Dict[str, object]):
        return Database(
            id=d["id"],
            object="database",
            created_time=datetime.strptime(d["created_time"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            last_edited_time=datetime.strptime(
                d["last_edited_time"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            title=RichText.from_dict(d["title"][0]),
            properties=dict(
                [
                    (k, database_property_from_dict(v))
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
    def from_dict(cls, d: Dict[str, object]):
        return PageObject(
            id=d["id"],
            object="page",
            archived=d["archived"],
            created_time=datetime.strptime(d["created_time"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            last_edited_time=datetime.strptime(
                d["last_edited_time"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            parent=PageParent.from_dict(d["parent"]),
            properties=dict(
                [(k, page_property_from_dict(v)) for (k, v) in d["properties"].items()]
            ),
        )
