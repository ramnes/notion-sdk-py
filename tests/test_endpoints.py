import pytest
import io


@pytest.mark.vcr()
def test_pages_create(client, parent_page_id):
    response = client.pages.create(
        parent={"page_id": parent_page_id},
        properties={
            "title": [{"text": {"content": "Test Page"}}],
        },
        children=[],
    )

    assert response["object"] == "page"

    # cleanup
    client.blocks.delete(block_id=response["id"])


@pytest.mark.vcr()
def test_pages_retrieve(client, page_id):
    response = client.pages.retrieve(page_id=page_id)
    assert response["object"] == "page"


@pytest.mark.vcr()
def test_pages_update(client, page_id):
    icon = {"type": "emoji", "emoji": "🛴"}

    response = client.pages.update(page_id=page_id, icon=icon)
    assert response["icon"]

    response = client.pages.update(page_id=page_id, icon=None)
    assert response["icon"] is None


@pytest.mark.vcr()
def test_pages_properties_retrieve(client, page_id):
    response = client.pages.properties.retrieve(page_id=page_id, property_id="title")
    assert response["results"][0]["type"] == "title"


@pytest.mark.vcr()
def test_blocks_children_create(client, page_id) -> str:
    children = [
        {"paragraph": {"rich_text": [{"text": {"content": "I'm a paragraph."}}]}}
    ]

    response = client.blocks.children.append(block_id=page_id, children=children)

    assert response["object"] == "list"
    assert len(response["results"]) > 0
    assert response["results"][0]["id"]


@pytest.mark.vcr()
def test_blocks_children_list(client, page_id):
    response = client.blocks.children.list(block_id=page_id)
    assert response["object"] == "list"
    assert response["type"] == "block"


@pytest.mark.vcr()
def test_blocks_retrieve(client, block_id):
    response = client.blocks.retrieve(block_id=block_id)
    assert response["object"] == "block"
    assert response["type"] == "paragraph"


@pytest.mark.vcr()
def test_blocks_update(client, block_id):
    new_plain_text = "I'm an updated paragraph."
    new_text = {
        "rich_text": [
            {
                "text": {"content": new_plain_text},
                "annotations": {"bold": True, "color": "red_background"},
            }
        ]
    }
    response = client.blocks.update(block_id=block_id, paragraph=new_text)

    assert response["paragraph"]["rich_text"][0]["plain_text"]


@pytest.mark.vcr()
def test_blocks_delete(client, block_id):
    client.blocks.delete(block_id=block_id)

    new_retrieve = client.blocks.retrieve(block_id=block_id)
    assert new_retrieve["archived"]

    client.blocks.update(block_id=block_id, archived=False)


@pytest.mark.vcr()
def test_users_list(client):
    response = client.users.list()
    assert response["type"] == "user"


@pytest.mark.vcr()
def test_users_me(client):
    response = client.users.me()
    assert response["type"] == "bot"
    assert response["id"]


@pytest.mark.vcr()
def test_users_retrieve(client):
    me = client.users.me()
    response = client.users.retrieve(me["id"])

    me.pop("request_id", None)
    response.pop("request_id", None)

    assert response == me


@pytest.mark.vcr()
def test_search(client, page_id):
    payload = {
        "query": page_id,
        "sort": {
            "direction": "descending",
            "timestamp": "last_edited_time",
        },
    }

    response = client.search(**payload)
    assert response["object"] == "list"


@pytest.mark.vcr()
def test_databases_create(client, page_id):
    properties = {
        "Name": {"title": {}},  # required property
    }
    title = [{"type": "text", "text": {"content": "Test Database"}}]
    parent = {"type": "page_id", "page_id": page_id}
    response = client.databases.create(
        **{"parent": parent, "title": title, "properties": properties}
    )

    assert response["object"] == "database"


@pytest.mark.vcr()
def test_databases_retrieve(client, database_id):
    response = client.databases.retrieve(database_id)
    assert response["object"] == "database"


@pytest.mark.vcr()
def test_databases_update(client, database_id):
    icon = {"type": "emoji", "emoji": "🔥"}

    response = client.databases.update(database_id=database_id, icon=icon)
    assert response["icon"]


@pytest.mark.vcr()
def test_data_sources_create(client, database_id):
    title = [{"type": "text", "text": {"content": "Test DataSource"}}]
    properties = {"Name": {"title": {}}}
    parent = {"type": "database_id", "database_id": database_id}
    response = client.data_sources.create(
        parent=parent, title=title, properties=properties
    )
    assert response["object"] == "data_source"


@pytest.mark.vcr()
def test_data_sources_retrieve(client, data_source_id):
    response = client.data_sources.retrieve(data_source_id)
    assert response["object"] == "data_source"


@pytest.mark.vcr()
def test_data_sources_query(client, data_source_id):
    response = client.data_sources.query(data_source_id)
    assert response["object"] == "list"


@pytest.mark.vcr()
def test_data_sources_update(client, data_source_id):
    new_title = [{"type": "text", "text": {"content": "Updated DataSource"}}]
    response = client.data_sources.update(data_source_id, title=new_title)
    assert response["object"] == "data_source"
    assert response["title"][0]["text"]["content"] == "Updated DataSource"


@pytest.mark.vcr()
def test_data_sources_list_templates(client, data_source_id):
    response = client.data_sources.list_templates(data_source_id=data_source_id)
    assert isinstance(response["templates"], list)
    assert isinstance(response["has_more"], bool)
    assert "next_cursor" in response


@pytest.mark.vcr()
def test_comments_create(client, page_id):
    parent = {"page_id": page_id}
    rich_text = [
        {
            "text": {
                "content": "This is a test comment.",
            },
        },
    ]

    response = client.comments.create(parent=parent, rich_text=rich_text)
    assert response


@pytest.mark.vcr()
def test_comments_list(client, page_id, comment_id):
    response = client.comments.list(block_id=page_id)
    assert response["object"] == "list"
    assert response["results"] != []


@pytest.mark.vcr()
def test_comments_retrieve(client, comment_id):
    response = client.comments.retrieve(comment_id=comment_id)
    assert response["object"] == "comment"
    assert response["id"] == comment_id


# Markdown endpoints require a public (OAuth) integration, so we can't record cassettes
# with our internal integration token. Using mocks instead.
def test_pages_retrieve_markdown(client, mocker):
    mock_response = {
        "object": "page_markdown",
        "id": "abc123",
        "markdown": "# Hello",
        "truncated": False,
        "unknown_block_ids": [],
    }
    mock_request = mocker.patch.object(client, "request", return_value=mock_response)

    response = client.pages.retrieve_markdown(page_id="abc123", include_transcript=True)

    assert response["object"] == "page_markdown"
    mock_request.assert_called_once_with(
        path="pages/abc123/markdown",
        method="GET",
        query={"include_transcript": True},
        auth=None,
    )


# Markdown endpoints require a public (OAuth) integration, so we can't record cassettes
# with our internal integration token. Using mocks instead.
def test_pages_update_markdown(client, mocker):
    mock_response = {
        "object": "page_markdown",
        "id": "abc123",
        "markdown": "## New Section\n\nHello from markdown.",
        "truncated": False,
        "unknown_block_ids": [],
    }
    mock_request = mocker.patch.object(client, "request", return_value=mock_response)

    response = client.pages.update_markdown(
        page_id="abc123",
        type="insert_content",
        insert_content={"content": "## New Section\n\nHello from markdown."},
    )

    assert response["object"] == "page_markdown"
    mock_request.assert_called_once_with(
        path="pages/abc123/markdown",
        method="PATCH",
        body={
            "type": "insert_content",
            "insert_content": {
                "content": "## New Section\n\nHello from markdown.",
            },
        },
        auth=None,
    )


@pytest.mark.vcr()
def test_pages_delete(client, page_id):
    response = client.blocks.delete(block_id=page_id)
    assert response

    client.pages.update(page_id=page_id, archived=False)


@pytest.mark.vcr()
def test_file_uploads_create(client):
    """Test creating a file upload"""
    response = client.file_uploads.create(
        mode="single_part", filename="test_file.txt", content_type="text/plain"
    )

    assert response["object"] == "file_upload"
    assert response["filename"] == "test_file.txt"
    assert response["content_type"] == "text/plain"
    assert "id" in response


@pytest.mark.vcr()
def test_file_uploads_create_multipart(client):
    """Test creating a multipart file upload"""
    response = client.file_uploads.create(
        mode="multi_part",
        filename="large_file.pdf",
        content_type="application/pdf",
        number_of_parts=3,
    )

    assert response["object"] == "file_upload"
    assert response["filename"] == "large_file.pdf"
    assert response["content_type"] == "application/pdf"
    assert response["number_of_parts"]["total"] == 3
    assert "id" in response


@pytest.mark.vcr()
def test_file_uploads_create_external(client):
    """Test creating an external file upload"""
    response = client.file_uploads.create(
        mode="external_url",
        filename="test_file.pdf",
        external_url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
    )

    assert response["object"] == "file_upload"
    assert response["filename"] == "test_file.pdf"
    assert "id" in response


@pytest.mark.vcr()
def test_file_uploads_retrieve(client, single_file_upload_id):
    """Test retrieving a file upload"""
    response = client.file_uploads.retrieve(file_upload_id=single_file_upload_id)

    assert response["object"] == "file_upload"
    assert response["id"] == single_file_upload_id
    assert response["filename"] == "test_file_small.txt"
    assert response["content_type"] == "text/plain"


@pytest.mark.vcr()
def test_file_uploads_list(client):
    """Test listing file uploads"""
    response = client.file_uploads.list()

    assert response["object"] == "list"
    assert response["type"] == "file_upload"
    assert isinstance(response["results"], list)
    assert isinstance(response["has_more"], bool)


@pytest.mark.vcr()
def test_file_uploads_list_with_status_filter(client, setup_file_uploads_ids):
    """Test listing file uploads with status filter"""
    _ = setup_file_uploads_ids
    response = client.file_uploads.list(status="pending")

    assert response["object"] == "list"
    assert response["type"] == "file_upload"
    assert isinstance(response["results"], list)
    assert all(upload["status"] == "pending" for upload in response["results"])


@pytest.mark.vcr()
def test_file_uploads_list_with_start_cursor(client, setup_file_uploads_ids):
    """Test listing file uploads with start cursor"""
    _ = setup_file_uploads_ids
    response_1 = client.file_uploads.list()

    response = client.file_uploads.list(start_cursor=response_1["results"][0]["id"])

    assert response["object"] == "list"
    assert response["type"] == "file_upload"
    assert isinstance(response["results"], list)
    assert isinstance(response["has_more"], bool)


@pytest.mark.vcr()
def test_file_uploads_list_with_pagination(client, setup_file_uploads_ids):
    """Test listing file uploads with pagination"""
    _ = setup_file_uploads_ids
    response = client.file_uploads.list(page_size=5)

    assert response["object"] == "list"
    assert response["type"] == "file_upload"
    assert isinstance(response["results"], list)
    assert len(response["results"]) <= 5


@pytest.mark.vcr()
def test_file_uploads_send(client, pending_single_file_upload_id):
    """Test sending a file upload"""
    # Create test file content
    test_content = b"This is test file content"
    file_obj = io.BytesIO(test_content)
    file_obj.name = "test_file_small.txt"

    # Send the file
    response = client.file_uploads.send(
        file_upload_id=pending_single_file_upload_id, file=file_obj
    )

    assert response["object"] == "file_upload"
    assert response["id"] == pending_single_file_upload_id
    assert response["status"] == "uploaded"
    assert response["filename"] == "test_file_small.txt"
    assert response["content_type"] == "text/plain"


@pytest.mark.vcr()
def test_file_uploads_send_multipart(client, pending_multi_file_upload_id):
    """Test sending a multipart file upload"""
    # Send first part
    test_content_part1 = b"A" * (10 * 1024 * 1024)
    file_part1 = io.BytesIO(test_content_part1)
    file_part1.name = "test_file_multi.txt.sf-part1"

    response = client.file_uploads.send(
        file_upload_id=pending_multi_file_upload_id, file=file_part1, part_number="1"
    )

    assert response["object"] == "file_upload"
    assert response["id"] == pending_multi_file_upload_id
    assert response["status"] == "pending"
    assert response["filename"] == "test_file_multi.txt"
    assert response["content_type"] == "text/plain"
    assert response["number_of_parts"]["total"] == 3
    assert response["number_of_parts"]["sent"] == 1


@pytest.mark.vcr()
def test_file_uploads_complete(client, part_uploaded_file_upload_id):
    """Test completing a file upload"""
    response = client.file_uploads.complete(file_upload_id=part_uploaded_file_upload_id)

    assert response["object"] == "file_upload"
    assert response["id"] == part_uploaded_file_upload_id
    assert response["status"] == "uploaded"
    assert response["filename"] == "test_file_multi.txt"
    assert response["content_type"] == "text/plain"
    assert response["number_of_parts"]["total"] == 3
    assert response["number_of_parts"]["sent"] == 3


def test_oauth_introspect(client, mocker):
    """Test OAuth token introspection with mock - tests Basic auth encoding"""
    mock_response = {"active": False, "request_id": "test-request-id"}

    mock_send = mocker.patch.object(
        client.client,
        "send",
        return_value=mocker.Mock(
            json=lambda: mock_response, raise_for_status=lambda: None
        ),
    )

    response = client.oauth.introspect(
        client_id="test_client_id",
        client_secret="test_client_secret",
        token="test_token",
    )

    assert "active" in response
    assert isinstance(response["active"], bool)

    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert "Authorization" in request.headers
    assert request.headers["Authorization"].startswith("Basic ")
    assert (
        request.headers["Authorization"]
        == "Basic dGVzdF9jbGllbnRfaWQ6dGVzdF9jbGllbnRfc2VjcmV0"
    )


def test_oauth_token_with_basic_auth(client, mocker):
    """Test OAuth token exchange with Basic auth - exercises auth encoding path"""
    mock_response = {
        "access_token": "secret_test_token",
        "token_type": "bearer",
        "bot_id": "bot_123",
    }

    mock_send = mocker.patch.object(
        client.client,
        "send",
        return_value=mocker.Mock(
            json=lambda: mock_response, raise_for_status=lambda: None
        ),
    )

    response = client.oauth.token(
        client_id="test_client_id",
        client_secret="test_client_secret",
        grant_type="authorization_code",
        code="test_code",
        redirect_uri="http://localhost:3000/callback",
    )

    assert response["access_token"] == "secret_test_token"

    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert "Authorization" in request.headers
    assert request.headers["Authorization"].startswith("Basic ")
    import base64

    expected = base64.b64encode(b"test_client_id:test_client_secret").decode()
    assert request.headers["Authorization"] == f"Basic {expected}"


def test_oauth_revoke_with_basic_auth(client, mocker):
    """Test OAuth revoke with Basic auth - exercises auth encoding path"""
    mock_response = {}

    mock_send = mocker.patch.object(
        client.client,
        "send",
        return_value=mocker.Mock(
            json=lambda: mock_response, raise_for_status=lambda: None
        ),
    )

    response = client.oauth.revoke(
        client_id="test_client_id",
        client_secret="test_client_secret",
        token="test_token",
    )

    assert response == {}

    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert "Authorization" in request.headers
    assert request.headers["Authorization"].startswith("Basic ")


def test_oauth_revoke(client, mocker):
    """Test OAuth token revocation with mock (can't use cassette - token becomes invalid)"""
    mock_response = {}
    mock_request = mocker.patch.object(client, "request", return_value=mock_response)

    response = client.oauth.revoke(
        client_id="test_client_id",
        client_secret="test_client_secret",
        token="test_token",
    )

    assert response == {}
    mock_request.assert_called_once_with(
        path="oauth/revoke",
        method="POST",
        body={"token": "test_token"},
        auth={"client_id": "test_client_id", "client_secret": "test_client_secret"},
    )


def test_oauth_token_authorization_code(client, mocker):
    mock_response = {
        "access_token": "secret_test_token",
        "token_type": "bearer",
        "bot_id": "bot_123",
        "workspace_id": "ws_456",
        "workspace_name": "Test Workspace",
        "owner": {"type": "user", "user": {"object": "user", "id": "user_789"}},
    }

    mock_request = mocker.patch.object(client, "request", return_value=mock_response)

    response = client.oauth.token(
        client_id="test_client_id",
        client_secret="test_client_secret",
        grant_type="authorization_code",
        code="test_code",
        redirect_uri="http://localhost:3000/callback",
    )

    assert response["access_token"] == "secret_test_token"
    assert response["bot_id"] == "bot_123"
    mock_request.assert_called_once()
    call_kwargs = mock_request.call_args[1]
    assert call_kwargs["path"] == "oauth/token"
    assert call_kwargs["method"] == "POST"
    assert call_kwargs["auth"] == {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
    }


def test_oauth_token_refresh_token(client, mocker):
    mock_response = {
        "access_token": "secret_refreshed_token",
        "token_type": "bearer",
        "bot_id": "bot_123",
    }

    mock_request = mocker.patch.object(client, "request", return_value=mock_response)

    response = client.oauth.token(
        client_id="test_client_id",
        client_secret="test_client_secret",
        grant_type="refresh_token",
        refresh_token="test_refresh_token",
    )

    assert response["access_token"] == "secret_refreshed_token"
    mock_request.assert_called_once()
    call_kwargs = mock_request.call_args[1]
    assert call_kwargs["path"] == "oauth/token"


@pytest.mark.vcr()
def test_move_pages(client, page_id):
    target_parent = client.pages.create(
        parent={"page_id": page_id},
        properties={"title": [{"text": {"content": "Target Parent"}}]},
    )

    page_to_move = client.pages.create(
        parent={"page_id": page_id},
        properties={"title": [{"text": {"content": "Moving Page"}}]},
    )

    response = client.pages.move(
        page_id=page_to_move["id"], parent={"page_id": target_parent["id"]}
    )

    assert response["object"] == "page"
    assert response["parent"]["page_id"] == target_parent["id"]
    assert response["id"] == page_to_move["id"]

    client.blocks.delete(block_id=page_to_move["id"])
    client.blocks.delete(block_id=target_parent["id"])
