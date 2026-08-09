"""The URL helpers must accept the host the Notion API actually returns.

Every object URL in this repo's own recorded cassettes is on `app.notion.com`, and the same
files carried `www.notion.so` before they were re-recorded. `get_id` raised and
`extract_notion_id` returned None for those URLs.
"""

import pathlib
import re

import pytest

import notion_client
from notion_client.helpers import extract_notion_id, extract_page_id, get_id

# Verbatim from tests/cassettes/, where it is the only object-URL host present.
API_PAGE_URL = "https://app.notion.com/p/393abc1eedcd80f3813be205934558c6"
EXPECTED_ID = "393abc1e-edcd-80f3-813b-e205934558c6"


def test_cassettes_really_do_use_this_host():
    """Guard: if the recorded responses stop using app.notion.com, the tests below are
    asserting against a host the API no longer returns and should be revisited. Without
    this the suite could keep passing while measuring nothing."""
    cassettes = pathlib.Path(notion_client.__file__).parents[1] / "tests" / "cassettes"
    hosts = set()
    for f in cassettes.glob("*.yaml"):
        hosts.update(
            re.findall(
                r'"(?:url|public_url)":"https://([^/"]+)', f.read_text(errors="ignore")
            )
        )
    assert hosts, (
        "no object URLs found in the cassettes; this test is measuring nothing"
    )
    assert hosts == {"app.notion.com"}, hosts


def test_get_id_accepts_the_host_the_api_returns():
    assert get_id(API_PAGE_URL) == EXPECTED_ID


def test_extract_notion_id_accepts_the_host_the_api_returns():
    assert extract_notion_id(API_PAGE_URL) == EXPECTED_ID
    assert extract_page_id(API_PAGE_URL) == EXPECTED_ID


@pytest.mark.parametrize(
    "url",
    [
        "https://notion.so/" + "a" * 32,
        "https://www.notion.so/" + "a" * 32,
        "https://app.notion.com/" + "a" * 32,
    ],
)
def test_notion_hosts_are_accepted(url):
    assert get_id(url) == "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    assert extract_notion_id(url) == "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"


@pytest.mark.parametrize(
    "url",
    [
        "https://evil.com/" + "a" * 32,
        "https://notion.so.evil.com/" + "a" * 32,
        "https://notion.com.evil.com/" + "a" * 32,
        "https://notsonotion.com/" + "a" * 32,
    ],
)
def test_non_notion_hosts_are_still_rejected(url):
    """The widened allowlist must not become a suffix match. These pass before the change
    and must keep passing after it."""
    with pytest.raises(ValueError):
        get_id(url)
    assert extract_notion_id(url) is None
