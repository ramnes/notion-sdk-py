from typing import TYPE_CHECKING, Any, Coroutine, Union

from httpx import Response

from notion_client.helpers import pick

if TYPE_CHECKING:
    from notion_client.client import AsyncClient, BaseClient, Client


class Endpoint:
    def __init__(self, parent: "BaseClient") -> None:
        self.parent = parent


class BlocksChildrenEndpoint(Endpoint):
    def append(
        self, block_id: str, **kwargs: Any
    ) -> Union[Response, Coroutine[Any, Any, Union[Response, Any]]]:
        return self.parent.request(
            path=f"blocks/{block_id}/children",
            method="PATCH",
            body=pick(kwargs, "children"),
        )

    def list(
        self, block_id: str, **kwargs: Any
    ) -> Union[Response, Coroutine[Any, Any, Union[Response, Any]]]:
        return self.parent.request(
            path=f"blocks/{block_id}/children",
            method="GET",
            query=pick(kwargs, "start_cursor", "page_size"),
        )


class BlocksEndpoint(Endpoint):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.children = BlocksChildrenEndpoint(*args, **kwargs)


class DatabasesEndpoint(Endpoint):
    def list(
        self, **kwargs: Any
    ) -> Union[Response, Coroutine[Any, Any, Union[Response, Any]]]:
        return self.parent.request(
            path="databases",
            method="GET",
            query=pick(kwargs, "start_cursor", "page_size"),
        )

    def query(
        self, database_id: str, **kwargs: Any
    ) -> Union[Response, Coroutine[Any, Any, Union[Response, Any]]]:
        return self.parent.request(
            path=f"databases/{database_id}/query",
            method="POST",
            body=pick(kwargs, "filter", "sorts", "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )

    def retrieve(
        self, database_id: str, **kwargs: Any
    ) -> Union[Response, Coroutine[Any, Any, Union[Response, Any]]]:
        return self.parent.request(
            path=f"databases/{database_id}",
            method="GET",
        )


class PagesEndpoint(Endpoint):
    def create(
        self, **kwargs: Any
    ) -> Union[Response, Coroutine[Any, Any, Union[Response, Any]]]:
        return self.parent.request(
            path="pages",
            method="POST",
            body=pick(kwargs, "parent", "properties", "children"),
        )

    def retrieve(
        self, page_id: str, **kwargs: Any
    ) -> Union[Response, Coroutine[Any, Any, Union[Response, Any]]]:
        return self.parent.request(
            path=f"pages/{page_id}",
            method="GET",
        )

    def update(
        self, page_id: str, **kwargs: Any
    ) -> Union[Response, Coroutine[Any, Any, Union[Response, Any]]]:
        return self.parent.request(
            path=f"pages/{page_id}", method="PATCH", body=pick(kwargs, "properties")
        )


class UsersEndpoint(Endpoint):
    def list(
        self, **kwargs: Any
    ) -> Union[Response, Coroutine[Any, Any, Union[Response, Any]]]:
        return self.parent.request(
            path="users",
            method="GET",
            query=pick(kwargs, "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )

    def retrieve(
        self, user_id: str, **kwargs: Any
    ) -> Union[Response, Coroutine[Any, Any, Union[Response, Any]]]:
        return self.parent.request(
            path=f"users/{user_id}",
            method="GET",
        )


class SearchEndpoint(Endpoint):
    def __call__(self, **kwargs: Any) -> Response:
        return self.parent.request(
            path="search",
            method="POST",
            body=pick(kwargs, "query", "sort", "filter", "start_cursor", "page_size"),
        )
