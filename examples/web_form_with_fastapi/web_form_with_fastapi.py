import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from notion_client import AsyncClient
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

notion = AsyncClient(auth=NOTION_API_KEY)

app = FastAPI()

HERE = Path(__file__).parent

app.mount("/public", StaticFiles(directory=str(HERE / "public")), name="public")


@app.get("/")
async def index():
    content = (HERE / "views" / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(content)


@app.post("/databases")
async def create_database(request: Request):
    body = await request.json()
    title = body.get("dbName", "")

    try:
        new_db = await notion.databases.create(
            parent={"type": "page_id", "page_id": NOTION_PAGE_ID},
            title=[{"type": "text", "text": {"content": title}}],
            properties={"Name": {"title": {}}},
        )

        if not is_full_database(new_db):
            return JSONResponse(
                {"message": "error", "error": "No read permissions on database"}
            )

        data_source_id = new_db["data_sources"][0]["id"]
        return JSONResponse(
            {
                "message": "success!",
                "data": {**new_db, "dataSourceId": data_source_id},
            }
        )
    except Exception as error:
        return JSONResponse({"message": "error", "error": str(error)})


@app.post("/pages")
async def create_page(request: Request):
    data = await request.json()
    db_id = data.get("dbID", "")
    page_name = data.get("pageName", "")
    header = data.get("header", "")

    try:
        new_page = await notion.pages.create(
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
        return JSONResponse({"message": "success!", "data": new_page})
    except Exception as error:
        return JSONResponse({"message": "error", "error": str(error)})


@app.post("/blocks")
async def create_block(request: Request):
    body = await request.json()
    page_id = body.get("pageID", "")
    content = body.get("content", "")

    try:
        new_block = await notion.blocks.children.append(
            block_id=page_id,
            children=[
                {
                    "paragraph": {
                        "rich_text": [{"text": {"content": content}}],
                    }
                }
            ],
        )
        return JSONResponse({"message": "success!", "data": new_block})
    except Exception as error:
        return JSONResponse({"message": "error", "error": str(error)})


@app.post("/comments")
async def create_comment(request: Request):
    body = await request.json()
    page_id = body.get("pageID", "")
    comment = body.get("comment", "")

    try:
        new_comment = await notion.comments.create(
            parent={"page_id": page_id},
            rich_text=[{"text": {"content": comment}}],
        )
        return JSONResponse({"message": "success!", "data": new_comment})
    except Exception as error:
        return JSONResponse({"message": "error", "error": str(error)})


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)
