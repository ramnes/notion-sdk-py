import os
import requests
import json

def make_request(query_param):
    api_key = os.getenv('BOOKS_API_KEY')
    headers = {
        'key': api_key
    }
    url = "https://www.googleapis.com/books/v1/volumes?q=" + query_param
    response = requests.request("GET", url, headers=headers, data={})
    return response.text

def get_book_details(title):
    book_details = json.loads(make_request(title))
    pruned_details = dict()
    try:
        volume_info = book_details['items'][0]['volumeInfo']
    except KeyError:
        print('No results found!')
        return {}

    keys = [
        'title',
        'authors',
        'description',
        'categories',
        'previewLink',
        'pageCount',
        'averageRating',
    ]

    existing_keys = [key for key in keys if key in volume_info.keys()]
    pruned_details.update({key:volume_info[key] for key in existing_keys})
    return pruned_details
