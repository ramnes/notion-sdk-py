"""Static typing regression tests (run mypy on small sample programs)."""

import pytest

mypy_api = pytest.importorskip("mypy.api")

SYNC = """
from notion_client import Client

client = Client(auth="x")
response = client.search(filter={"property": "object", "value": "page"})
results = response["results"]
"""

ASYNC = """
from notion_client import AsyncClient

async def main() -> None:
    client = AsyncClient(auth="x")
    response = await client.search()
    results = response["results"]
"""

ASYNC_MISSING_AWAIT = """
from notion_client import AsyncClient

async def main() -> None:
    client = AsyncClient(auth="x")
    client.search()["results"]
"""


def run_mypy(tmp_path, source):
    path = tmp_path / "sample.py"
    path.write_text(source)
    stdout, _, status = mypy_api.run([str(path), "--no-incremental"])
    return stdout, status


def test_sync_client_response_is_indexable(tmp_path):
    stdout, status = run_mypy(tmp_path, SYNC)
    assert status == 0, stdout


def test_async_client_awaited_response_is_indexable(tmp_path):
    stdout, status = run_mypy(tmp_path, ASYNC)
    assert status == 0, stdout


def test_async_client_missing_await_is_an_error(tmp_path):
    stdout, status = run_mypy(tmp_path, ASYNC_MISSING_AWAIT)
    assert status == 1 and "not indexable" in stdout
