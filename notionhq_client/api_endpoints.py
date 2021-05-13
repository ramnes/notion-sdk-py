from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client


class Endpoint:

    def __init__(self, parent: "Client"):
        self.parent = parent


class UsersEndpoint(Endpoint):

    def list(self, **kwargs):
        return self.parent.request(
            path="users",
            method="GET",
            query={
                key: kwargs.get(key)
                for key in ("start_cursor", "page_size")
            },
            auth=kwargs.get("auth")
        )


class DatabasesEndpoint(Endpoint):

    def query(self, database_id, **kwargs):
        return self.parent.request(
            path=f"databases/{database_id}/query",
            method="POST",
            body={
                key: kwargs.get(key)
                for key in ("filter", "sorts", "start_cursor", "page_size")
            },
            auth=kwargs.get("auth")
        )
