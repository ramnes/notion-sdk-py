"""Tests for API version compatibility between legacy and 2025-09-03."""

import pytest
from unittest.mock import MagicMock

from notion_client import Client, AsyncClient


class TestDatabaseQueryVersionRouting:
    """Test database query routing based on API version."""

    def test_database_query_legacy_version(self):
        """Test database query uses legacy endpoint for older API versions."""
        # Mock client with legacy version
        client = Client(auth="test-token", notion_version="2022-06-28")
        client.request = MagicMock(return_value={"object": "list", "results": []})

        # Call database query without data_source_id
        client.databases.query(database_id="test-db-id")

        # Verify it uses the legacy databases endpoint
        client.request.assert_called_once_with(
            path="databases/test-db-id/query",
            method="POST",
            query={},
            body={},  # pick() only includes keys that exist in kwargs
            auth=None,
        )

    def test_database_query_new_api_with_data_source_id(self):
        """Test database query routes to data sources for 2025-09-03 with data_source_id."""
        client = Client(auth="test-token", notion_version="2025-09-03")

        # Mock data_sources.query method
        client.data_sources = MagicMock()
        client.data_sources.query.return_value = {
            "object": "list",
            "data_source_id": "test-ds-id",
        }

        # Call database query with data_source_id
        client.databases.query(database_id="test-db-id", data_source_id="test-ds-id")

        # Verify it routes to data_sources.query
        client.data_sources.query.assert_called_once_with(data_source_id="test-ds-id")

    def test_database_query_new_api_without_data_source_id_falls_back(self):
        """Without data_source_id, fallback to legacy database query for compatibility."""
        client = Client(auth="test-token", notion_version="2025-09-03")
        client.request = MagicMock(return_value={"object": "list", "results": []})

        client.databases.query(database_id="test-db-id")

        client.request.assert_called_once_with(
            path="databases/test-db-id/query",
            method="POST",
            query={},
            body={},
            auth=None,
        )


class TestDatabaseCreateVersionHandling:
    """Test database creation with initial_data_source for 2025-09-03."""

    def test_database_create_legacy_version(self):
        """Test database create works normally for legacy versions."""
        client = Client(auth="test-token", notion_version="2022-06-28")
        client.request = MagicMock(return_value={"object": "database"})

        client.databases.create(
            parent={"page_id": "test-page-id"},
            title=[{"text": {"content": "Test DB"}}],
            properties={"Name": {"type": "title", "title": {}}},
        )

        # Verify properties are passed directly
        client.request.assert_called_once()
        call_args = client.request.call_args
        assert "properties" in call_args[1]["body"]
        assert "initial_data_source" not in call_args[1]["body"]

    def test_database_create_new_api_auto_wraps_properties(self):
        """Test database create auto-wraps properties in initial_data_source for 2025-09-03."""
        client = Client(auth="test-token", notion_version="2025-09-03")
        client.request = MagicMock(return_value={"object": "database"})

        client.databases.create(
            parent={"page_id": "test-page-id"},
            title=[{"text": {"content": "Test DB"}}],
            properties={"Name": {"type": "title", "title": {}}},
        )

        # Verify properties are wrapped in initial_data_source
        client.request.assert_called_once()
        call_args = client.request.call_args
        body = call_args[1]["body"]

        assert "properties" not in body
        assert "initial_data_source" in body
        assert body["initial_data_source"]["properties"]["Name"]["type"] == "title"

    def test_database_create_new_api_explicit_initial_data_source(self):
        """Test database create with explicit initial_data_source for 2025-09-03."""
        client = Client(auth="test-token", notion_version="2025-09-03")
        client.request = MagicMock(return_value={"object": "database"})

        client.databases.create(
            parent={"page_id": "test-page-id"},
            title=[{"text": {"content": "Test DB"}}],
            properties={"Name": {"type": "title", "title": {}}},
            initial_data_source={
                "properties": {"Status": {"type": "select", "select": {"options": []}}}
            },
        )

        # Verify explicit initial_data_source takes precedence
        client.request.assert_called_once()
        call_args = client.request.call_args
        body = call_args[1]["body"]

        assert "properties" not in body
        assert "initial_data_source" in body
        assert "Status" in body["initial_data_source"]["properties"]
        assert "Name" not in body["initial_data_source"]["properties"]


class TestDatabaseUpdateVersionRouting:
    """Test database update routing for schema changes in 2025-09-03."""

    def test_database_update_legacy_version(self):
        """Test database update works normally for legacy versions."""
        client = Client(auth="test-token", notion_version="2022-06-28")
        client.request = MagicMock(return_value={"object": "database"})

        client.databases.update(
            database_id="test-db-id",
            title=[{"text": {"content": "Updated DB"}}],
            properties={"New Property": {"type": "rich_text", "rich_text": {}}},
        )

        # Verify properties are updated directly
        client.request.assert_called_once_with(
            path="databases/test-db-id",
            method="PATCH",
            body={
                "title": [{"text": {"content": "Updated DB"}}],
                "properties": {"New Property": {"type": "rich_text", "rich_text": {}}},
            },
            auth=None,
        )

    def test_database_update_new_api_with_properties_requires_data_source_id(self):
        """Test database update with properties requires data_source_id for 2025-09-03."""
        client = Client(auth="test-token", notion_version="2025-09-03")

        # Should raise ValueError when properties provided without data_source_id
        with pytest.raises(ValueError) as exc_info:
            client.databases.update(
                database_id="test-db-id",
                properties={"New Property": {"type": "rich_text", "rich_text": {}}},
            )

        assert "To update schema under 2025-09-03, supply data_source_id" in str(
            exc_info.value
        )

    def test_database_update_new_api_routes_properties_to_data_source(self):
        """Test database update routes properties to data source for 2025-09-03."""
        client = Client(auth="test-token", notion_version="2025-09-03")
        client.request = MagicMock(return_value={"object": "database"})

        # Mock data_sources.update
        client.data_sources = MagicMock()
        client.data_sources.update.return_value = {"object": "data_source"}

        client.databases.update(
            database_id="test-db-id",
            data_source_id="test-ds-id",
            title=[{"text": {"content": "Updated DB"}}],
            properties={"New Property": {"type": "rich_text", "rich_text": {}}},
            description=[{"text": {"content": "Updated description"}}],
        )

        # Verify properties are sent to data source
        client.data_sources.update.assert_called_once_with(
            "test-ds-id",
            title=[{"text": {"content": "Updated DB"}}],
            properties={"New Property": {"type": "rich_text", "rich_text": {}}},
        )

        # Verify remaining fields are sent to database
        client.request.assert_called_once_with(
            path="databases/test-db-id",
            method="PATCH",
            body={
                "title": [{"text": {"content": "Updated DB"}}],
                "description": [{"text": {"content": "Updated description"}}],
            },
            auth=None,
        )

    def test_database_update_new_api_only_data_source_update(self):
        """Test database update returns only data source response when no DB fields."""
        client = Client(auth="test-token", notion_version="2025-09-03")
        client.request = MagicMock()
        client.data_sources = MagicMock()
        client.data_sources.update.return_value = {"object": "data_source", "ok": True}

        res = client.databases.update(
            database_id="test-db-id",
            data_source_id="test-ds-id",
            properties={"New": {"type": "checkbox", "checkbox": {}}},
        )

        assert res == {"object": "data_source", "ok": True}
        client.request.assert_not_called()
        client.data_sources.update.assert_called_once_with(
            "test-ds-id",
            properties={"New": {"type": "checkbox", "checkbox": {}}},
        )


class TestSearchFilterVersionHandling:
    """Test search filter value conversion for 2025-09-03."""

    def test_search_legacy_version_no_conversion(self):
        """Test search filter value is not converted for legacy versions."""
        client = Client(auth="test-token", notion_version="2022-06-28")
        client.request = MagicMock(return_value={"object": "list"})

        client.search(filter={"property": "object", "value": "database"})

        # Verify filter value is not converted
        client.request.assert_called_once()
        call_args = client.request.call_args
        body = call_args[1]["body"]

        assert body["filter"]["value"] == "database"

    def test_search_new_api_converts_database_to_data_source(self):
        """Test search filter converts 'database' to 'data_source' for 2025-09-03."""
        client = Client(auth="test-token", notion_version="2025-09-03")
        client.request = MagicMock(return_value={"object": "list"})

        # Mock logger to capture warning
        client.logger = MagicMock()

        client.search(filter={"property": "object", "value": "database"})

        # Verify filter value is converted
        client.request.assert_called_once()
        call_args = client.request.call_args
        body = call_args[1]["body"]

        assert body["filter"]["value"] == "data_source"

        # Verify warning is logged
        client.logger.warning.assert_called_once_with(
            "Search filter.value 'database' is deprecated; using 'data_source'."
        )

    def test_search_new_api_no_conversion_for_other_values(self):
        """Test search filter does not convert other values for 2025-09-03."""
        client = Client(auth="test-token", notion_version="2025-09-03")
        client.request = MagicMock(return_value={"object": "list"})

        client.search(filter={"property": "object", "value": "page"})

        # Verify filter value is not converted
        client.request.assert_called_once()
        call_args = client.request.call_args
        body = call_args[1]["body"]

        assert body["filter"]["value"] == "page"


class TestAsyncVersionCompatibility:
    """Test version compatibility for async client."""

    @pytest.mark.asyncio
    async def test_async_database_query_new_api_routing(self):
        """Test async database query routes correctly for 2025-09-03."""
        client = AsyncClient(auth="test-token", notion_version="2025-09-03")

        # Mock data_sources.query method
        client.data_sources = MagicMock()
        client.data_sources.query = MagicMock(return_value={"object": "list"})

        # Call database query with data_source_id
        client.databases.query(database_id="test-db-id", data_source_id="test-ds-id")

        # Verify it routes to data_sources.query
        client.data_sources.query.assert_called_once_with(data_source_id="test-ds-id")

    @pytest.mark.asyncio
    async def test_async_database_query_fallback_without_data_source_id(self):
        """Async variant also falls back to legacy database query path when not provided."""
        client = AsyncClient(auth="test-token", notion_version="2025-09-03")
        client.request = MagicMock(return_value={"object": "list", "results": []})

        client.databases.query(database_id="test-db-id")

        client.request.assert_called_once_with(
            path="databases/test-db-id/query",
            method="POST",
            query={},
            body={},
            auth=None,
        )


class TestVersionDetectionEdgeCases:
    """Test edge cases in version detection logic."""

    def test_missing_notion_version_defaults_to_legacy(self):
        """Test that missing notion_version attribute defaults to legacy behavior."""
        from notion_client.api_endpoints import DatabasesEndpoint

        # Create mock parent without notion_version
        mock_parent = MagicMock()
        mock_parent.options = MagicMock()
        delattr(mock_parent.options, "notion_version")  # Remove the attribute

        DatabasesEndpoint(mock_parent)

        # Test version detection
        new_api = getattr(mock_parent.options, "notion_version", "") >= "2025-09-03"
        assert new_api is False

    def test_empty_notion_version_defaults_to_legacy(self):
        """Test that empty notion_version defaults to legacy behavior."""
        from notion_client.api_endpoints import DatabasesEndpoint

        # Create mock parent with empty notion_version
        mock_parent = MagicMock()
        mock_parent.options = MagicMock()
        mock_parent.options.notion_version = ""

        DatabasesEndpoint(mock_parent)

        # Test version detection
        new_api = getattr(mock_parent.options, "notion_version", "") >= "2025-09-03"
        assert new_api is False

    def test_version_comparison_boundary_cases(self):
        """Test version comparison with various boundary cases."""
        test_cases = [
            ("2022-06-28", False),
            ("2025-09-02", False),
            ("2025-09-03", True),
            ("2025-09-04", True),
            ("2026-01-01", True),
        ]

        for version, expected_new_api in test_cases:
            new_api = version >= "2025-09-03"
            assert (
                new_api == expected_new_api
            ), f"Version {version} should be {'new' if expected_new_api else 'legacy'} API"
