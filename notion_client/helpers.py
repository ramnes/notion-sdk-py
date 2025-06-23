"""Utility functions for notion-sdk-py."""
import os
import asyncio
from typing import Any, AsyncGenerator, Awaitable, Callable, Dict, Generator, List
from urllib.parse import urlparse
from uuid import UUID

def pick(base: Dict[Any, Any], *keys: str) -> Dict[Any, Any]:
    """Return a dict composed of key value pairs for keys passed as args."""
    result = {}
    for key in keys:
        if key not in base:
            continue
        value = base.get(key)
        if value is None and key == "start_cursor":
            continue
        result[key] = value
    return result


def get_url(object_id: str) -> str:
    """Return the URL for the object with the given id."""
    return f"https://notion.so/{UUID(object_id).hex}"


def get_id(url: str) -> str:
    """Return the id of the object behind the given URL."""
    parsed = urlparse(url)
    if parsed.netloc not in ("notion.so", "www.notion.so"):
        raise ValueError("Not a valid Notion URL.")
    path = parsed.path
    if len(path) < 32:
        raise ValueError("The path in the URL seems to be incorrect.")
    raw_id = path[-32:]
    return str(UUID(raw_id))


def iterate_paginated_api(
    function: Callable[..., Any], **kwargs: Any
) -> Generator[Any, None, None]:
    """Return an iterator over the results of any paginated Notion API."""
    next_cursor = kwargs.pop("start_cursor", None)

    while True:
        response = function(**kwargs, start_cursor=next_cursor)
        for result in response.get("results"):
            yield result

        next_cursor = response.get("next_cursor")
        if not response.get("has_more") or not next_cursor:
            return


def collect_paginated_api(function: Callable[..., Any], **kwargs: Any) -> List[Any]:
    """Collect all the results of paginating an API into a list."""
    return [result for result in iterate_paginated_api(function, **kwargs)]


async def async_iterate_paginated_api(
    function: Callable[..., Awaitable[Any]], **kwargs: Any
) -> AsyncGenerator[Any, None]:
    """Return an async iterator over the results of any paginated Notion API."""
    next_cursor = kwargs.pop("start_cursor", None)

    while True:
        response = await function(**kwargs, start_cursor=next_cursor)
        for result in response.get("results"):
            yield result

        next_cursor = response.get("next_cursor")
        if (not response["has_more"]) | (next_cursor is None):
            return


async def async_collect_paginated_api(
    function: Callable[..., Awaitable[Any]], **kwargs: Any
) -> List[Any]:
    """Collect asynchronously all the results of paginating an API into a list."""
    return [result async for result in async_iterate_paginated_api(function, **kwargs)]


def is_full_block(response: Dict[Any, Any]) -> bool:
    """Return `True` if response is a full block."""
    return response.get("object") == "block" and "type" in response


def is_full_page(response: Dict[Any, Any]) -> bool:
    """Return `True` if response is a full page."""
    return response.get("object") == "page" and "url" in response


def is_full_database(response: Dict[Any, Any]) -> bool:
    """Return `True` if response is a full database."""
    return response.get("object") == "database" and "title" in response


def is_full_page_or_database(response: Dict[Any, Any]) -> bool:
    """Return `True` if `response` is a full database or a full page."""
    if response.get("object") == "database":
        return is_full_database(response)
    return is_full_page(response)


def is_full_user(response: Dict[Any, Any]) -> bool:
    """Return `True` if response is a full user."""
    return "type" in response


def is_full_comment(response: Dict[Any, Any]) -> bool:
    """Return `True` if response is a full comment."""
    return "type" in response


def is_text_rich_text_item_response(rich_text: Dict[Any, Any]) -> bool:
    """Return `True` if `rich_text` is a text."""
    return rich_text.get("type") == "text"


def is_equation_rich_text_item_response(rich_text: Dict[Any, Any]) -> bool:
    """Return `True` if `rich_text` is an equation."""
    return rich_text.get("type") == "equation"


def is_mention_rich_text_item_response(rich_text: Dict[Any, Any]) -> bool:
    """Return `True` if `rich_text` is a mention."""
    return rich_text.get("type") == "mention"

def split_file(file_path: str, chunk_size: int = 1024 * 1024 * 10) -> List[str]:
    """
    Split a file into chunks of a specified size.

    Args:
        file_path: Path to the input file (can be relative to the project).
        chunk_size: Size of each chunk in bytes.

    Returns:
        A list of file paths for the resulting chunks.
    """

    output_filenames = []

    # Get the file name
    file_name = os.path.basename(file_path)
    file_name_without_extention, _ = os.path.splitext(
        file_name
    )  # Remove file extension
    # create a directory for the split files
    file_split_name = file_name_without_extention + "_split"
    file_dir = os.path.join(os.path.dirname(file_path), file_split_name)
    os.makedirs(file_dir, exist_ok=True)  # create directory if it does not exist

    with open(file_path, "rb") as f:
        part_num = 1
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break

            # Generate chunk file names
            part_file_name = f"{file_name}.sf-part{part_num}"
            part_file_path = os.path.join(file_dir, part_file_name)

            # Write chunk files
            with open(part_file_path, "wb") as part_file:
                part_file.write(chunk)

            output_filenames.append(part_file_path)
            part_num += 1

    return output_filenames


async def split_file_async(
    file_path: str, chunk_size: int = 1024 * 1024 * 10
) -> List[str]:
    """
    Asynchronous version of the file splitting function.

    Args:
        file_path: Path to the input file (can be relative to the project).
        chunk_size: Size of each chunk in bytes.

    Returns:
        A list of file paths for the resulting chunks.
    """
    return await asyncio.get_event_loop().run_in_executor(
        None, split_file, file_path, chunk_size
    )
