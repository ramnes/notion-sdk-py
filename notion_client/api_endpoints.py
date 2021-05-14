from typing import TYPE_CHECKING

from .helpers import pick

if TYPE_CHECKING:
    from .client import Client


class Endpoint:
    def __init__(self, parent: "Client"):
        self.parent = parent


class BlocksChildrenEndpoint(Endpoint):
    def append(self, block_id, **kwargs):
        return self.parent.request(
            path=f"blocks/{block_id}/children",
            method="PATCH",
            body=pick(kwargs, "children"),
        )

    def list(self, block_id, **kwargs):
        return self.parent.request(
            path=f"blocks/{block_id}/children",
            method="GET",
            query=pick(kwargs, "start_cursor", "page_size"),
        )


class BlocksEndpoint(Endpoint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = BlocksChildrenEndpoint(*args, **kwargs)


class DatabasesEndpoint(Endpoint):
    def list(self, **kwargs):
        return self.parent.request(
            path="databases",
            method="GET",
            query=pick(kwargs, "start_cursor", "page_size"),
        )

    def query(self, database_id, **kwargs):
        return self.parent.request(
            path=f"databases/{database_id}/query",
            method="POST",
            body=pick(kwargs, "filter", "sorts", "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )

    def retrieve(self, database_id, **kwargs):
        return self.parent.request(
            path=f"databases/{database_id}",
            method="GET",
        )


class PagesEndpoint(Endpoint):
    def create(self, **kwargs):
        return self.parent.request(
            path="pages",
            method="POST",
            body=pick(kwargs, "parent", "properties", "children"),
        )

    def retrieve(self, page_id, **kwargs):
        return self.parent.request(
            path=f"pages/{page_id}",
            method="GET",
        )

    def update(self, page_id, **kwargs):
        return self.parent.request(
            path=f"pages/{page_id}", method="PATCH", body=pick(kwargs, "properties")
        )


class UsersEndpoint(Endpoint):
    def list(self, **kwargs):
        return self.parent.request(
            path="users",
            method="GET",
            query=pick(kwargs, "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )

    def retrieve(self, user_id, **kwargs):
        return self.parent.request(
            path=f"users/{user_id}",
            method="GET",
        )
