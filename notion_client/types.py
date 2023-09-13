"""The types for the various responses."""

from typing import Literal, TypedDict, Union


class EmptyObject(TypedDict):
    ...


# ---------- User ----------


class PersonDetails(TypedDict):
    email: str | None


class PersonUserObjectResponse(TypedDict):
    type: Literal["person"]
    person: PersonDetails
    name: str | None
    avatar_url: str | None
    id: str
    object: Literal["user"]


class WorkspaceOwner(TypedDict):
    type: Literal["workspace"]
    workspace: Literal[True]


class BotDetails(TypedDict):
    owner: PersonUserObjectResponse | WorkspaceOwner
    workspace_name: str | None


class BotUserObjectResponse(TypedDict):
    type: Literal["bot"]
    bot: EmptyObject | BotDetails
    name: str | None
    avatar_url: str | None
    id: str
    object: Literal["user"]


UserObjectResponse = Union[PersonUserObjectResponse, BotUserObjectResponse]
