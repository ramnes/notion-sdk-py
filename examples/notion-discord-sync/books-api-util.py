
import os
import requests
import json

def make_request(query_param):
    api_key = os.getenv('BOOKS_API_KEY')
    headers = {
        'key': api_key
    }
    url = "https://www.googleapis.com/books/v1/volumes?q="+query_param
    response = requests.request("GET", url, headers=headers, data={})
    return response.text

def get_book_details(title):
    book_details = json.loads(make_request(title))
    pruned_details = dict()
    volume_info = book_details['items'][0]['volumeInfo']
    pruned_details = {key:volume_info[key] for key in [
        'title',
        'authors',
        'pageCount',
        'description',
        'categories',
        'averageRating',
        'previewLink'
    ]}
    return pruned_details

print(get_book_details('1984'))