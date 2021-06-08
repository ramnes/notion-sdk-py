import os

import pytest


@pytest.fixture(scope="session")
def token():
    return os.environ["NOTION_TOKEN"]
