import os
import logging
from notion_client import Client, errors
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
def is_valid(details_dict, key):
    return key in details_dict.keys()

def add_author(details_dict, authors):
    details_dict['properties'].update({
        "Authors": 
        {
            "rich_text": [
                {
                    "text": {
                        "content":  ", ".join(authors)
                    }
                }
            ]
        },
    })

def add_page_count(details_dict, page_count):
    details_dict['properties'].update({
        "Length": {
            "number": page_count
        },
    })

def add_rating(details_dict, rating):
    details_dict['properties'].update({
        "Rating": {
            "number": rating
        },
    })

def add_preview_link(details_dict, preview_link):
    details_dict['properties'].update({
        "Preview Link": 
            {
                "rich_text": [
                    {
                        "text": {
                            "content": preview_link
                        }
                    }
                ]
            }
    })

def transform_book_details(details, db_id):
    logging.debug(details)
    notion_book_page = {
        "parent": {
            "database_id": db_id
        },
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": details["title"]
                        }
                    }
                ]
            },
        }
    }
    keys = ["authors", "pageCount", "rating", "previewLink"]

    is_valid(details, "authors") and add_author(notion_book_page, details["authors"])
    is_valid(details, "pageCount") and add_page_count(notion_book_page, details["pageCount"])
    is_valid(details, "averageRating") and add_rating(notion_book_page, details["averageRating"])
    is_valid(details, "previewLink") and add_preview_link(notion_book_page, details["previewLink"])
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
            if response.status_code == 200:
                return True
            else:
                return False
        # if there is an exception while writing to the Notion database, flag as failure
        except errors.APIResponseError as error:
            logging.exception("Updating Notion database failed because of exception %s"%(error.message))
            return False
    # if there is no response from Google Books API, then flag as failure
    else:
        return False
