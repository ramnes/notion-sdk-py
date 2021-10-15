import pytest

from examples.databases.create_database import create_database, manual_inputs


@pytest.mark.vcr()
def test_create_database():
    new_db = create_database(
        parent_id="08a6286e3aaf4adcbee89ba2537d1954", db_name="test9"
    )
    assert new_db["object"] == "database"


# just for the sake of code coverage
def test_manual_inputs():
    assert manual_inputs("test1", "test2") == ("test1", "test2")
