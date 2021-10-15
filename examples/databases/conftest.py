import pytest


@pytest.fixture(scope="session")
def vcr_config():
    def remove_headers(response):
        response["headers"] = {}
        return response

    return {
        "filter_headers": [("authorization", "secret_..."), ("user-agent", None)],
        "before_record_response": remove_headers,
    }
