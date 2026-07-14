import os

from flask import Flask, jsonify, request, send_from_directory
from notion_client import Client
from notion_client.helpers import is_full_database

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    pass
else:
    load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID", "")

while NOTION_API_KEY == "":
    NOTION_API_KEY = input("Enter your Notion integration token: ").strip()
while NOTION_PAGE_ID == "":
    NOTION_PAGE_ID = input("Enter the Notion page ID: ").strip()

notion = Client(auth=NOTION_API_KEY)

app = Flask(__name__, static_folder="public", static_url_path="")


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/databases", methods=["POST"])
def create_database():
    page_id = NOTION_PAGE_ID
    title = request.json.get("dbName", "")

    try:
        new_db = notion.databases.create(
            parent={"type": "page_id", "page_id": page_id},
            title=[{"type": "text", "text": {"content": title}}],
            properties={"Name": {"title": {}}},
        )

        if not is_full_database(new_db):
            return jsonify(
                {"message": "error", "error": "No read permissions on database"}
            )

        data_source_id = new_db["data_sources"][0]["id"]
        return jsonify(
            {
                "message": "success!",
                "data": {**new_db, "dataSourceId": data_source_id},
            }
        )
    except Exception as error:
        return jsonify({"message": "error", "error": str(error)})


@app.route("/pages", methods=["POST"])
def create_page():
    data = request.json
    db_id = data.get("dbID", "")
    page_name = data.get("pageName", "")
    header = data.get("header", "")

    try:
        new_page = notion.pages.create(
            parent={"type": "data_source_id", "data_source_id": db_id},
            properties={
                "Name": {
                    "title": [{"text": {"content": page_name}}],
                }
            },
            children=[
                {
                    "object": "block",
                    "heading_2": {
                        "rich_text": [{"text": {"content": header}}],
                    },
                }
            ],
        )
        return jsonify({"message": "success!", "data": new_page})
    except Exception as error:
        return jsonify({"message": "error", "error": str(error)})


@app.route("/blocks", methods=["POST"])
def create_block():
    page_id = request.json.get("pageID", "")
    content = request.json.get("content", "")

    try:
        new_block = notion.blocks.children.append(
            block_id=page_id,
            children=[
                {
                    "paragraph": {
                        "rich_text": [{"text": {"content": content}}],
                    }
                }
            ],
        )
        return jsonify({"message": "success!", "data": new_block})
    except Exception as error:
        return jsonify({"message": "error", "error": str(error)})


@app.route("/comments", methods=["POST"])
def create_comment():
    page_id = request.json.get("pageID", "")
    comment = request.json.get("comment", "")

    try:
        new_comment = notion.comments.create(
            parent={"page_id": page_id},
            rich_text=[{"text": {"content": comment}}],
        )
        return jsonify({"message": "success!", "data": new_comment})
    except Exception as error:
        return jsonify({"message": "error", "error": str(error)})


if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT", 3000)))
