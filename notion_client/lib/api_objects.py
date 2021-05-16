from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from custom_enums import ParentType
from property import database_property_from_dict, DatabaseProperty
from property_values import page_property_from_dict
from datatypes import RichText


@dataclass
class APIObject:
    id: str
    object: str
    created_time: datetime
    last_edited_time: datetime


@dataclass
class DatabaseObject(APIObject):
    title: List[RichText]
    properties: Dict[str, DatabaseProperty]

    @classmethod
    def from_dict(cls, d: Dict[str, object]):
        return DatabaseObject(
            id=d['id'],
            object="database",
            created_time=datetime.strptime(d['created_time'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            last_edited_time=datetime.strptime(d['last_edited_time'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            title=RichText.from_dict(d['title'][0]),
            properties=dict([
                (k, database_property_from_dict(v)) for (k, v) in d["properties"].items()
            ])
        )

@dataclass
class PageParent:
    type: ParentType
    id: str

    @classmethod
    def from_dict(cls, d: Dict[str, object]):
        type = ParentType(d['type'])
        return PageParent(
            id=d.get("database_id" if type == ParentType.database else "page_id"),
            type=type,
        )

@dataclass
class PageObject(APIObject):
    parent: PageParent
    archived: bool
    properties: Dict[str, DatabaseProperty]


    @classmethod
    def from_dict(cls, d: Dict[str, object]):
        return PageObject(
            id=d['id'],
            object="page",
            archived=d['archived'],
            created_time=datetime.strptime(d['created_time'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            last_edited_time=datetime.strptime(d['last_edited_time'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            parent=PageParent.from_dict(d['parent']),
            properties=dict([
                (k, page_property_from_dict(v)) for (k, v) in d["properties"].items()
            ])
        )
