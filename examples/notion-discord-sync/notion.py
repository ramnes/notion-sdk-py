import os
import logging
from notion_client import Client, errors
from pprint import pprint
import json
from books_api_util import get_book_details

# transform Google Books API response to Notion Page
# these properties are based on the Notion database used for this project, you can find a template in the README
# the book details we will be using:
# details : {
#   title: (string) name of the book,
#   authors: (array) authors,
#   pageCount: (number) number of pages,
#   averageRating: (number) rating on Google Books 0-5
#   previewLink: (string) Google Books preview URL
# }
def transform_book_details(details, db_id):
    logging.debug(details)
    notion_book_page = {
        "parent": {
            "database_id": db_id
        },
        "properties": {
            "Authors": 
            {
                "rich_text": [
                    {
                        "text": {
                            "content": ", ".join(details["authors"])
                        }
                    }
                ]
            },
            "Length": {
                "number": details["pageCount"]
            },
            "Rating": {
                "number": details["averageRating"]
            },
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": details["title"]
                        }
                    }
                ]
            },
            "Preview Link": 
            {
                "rich_text": [
                    {
                        "text": {
                            "content": details["previewLink"]
                        }
                    }
                ]
            }
        }
    }
    logging.debug(notion_book_page)
    return notion_book_page


def add_recommendation(recommended_book):
    db_id = os.getenv('DATABASE_ID')
    notion = Client(auth=os.getenv('NOTION_TOKEN'), log_level=logging.INFO)
    # search Google Books API for the book recommendation
    book_details_google_books_api_format = get_book_details(recommended_book)
    if len(book_details_google_books_api_format):
        # transform the book details to the appropriate Notion page format
        notion_book_page = transform_book_details(book_details_google_books_api_format, db_id)
        try:
            response = notion.pages.create(
                **notion_book_page
            )
            return True
        # if there is an exception while writing to the Notion database, flag as failure
        except errors.APIResponseError as error:
            logging.exception("Updating Notion database failed because of exception %s"%(error.message))
            return False
    # if there is incomplete/no response from Google Books API, then flag as failure
    else:
        return False
