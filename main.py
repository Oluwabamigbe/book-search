import requests


def get_books(query):
    url = "https://openlibrary.org/search.json"

    params = {
        "q": query,
        "fields": "title,author_name,first_publish_year,key",
        "limit": 10
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    return data["docs"]


query = input("Search for a book: ")

books = get_books(query)

print("\nResults:")

for book in books:
    title = book.get("title", "Unknown title")

    authors = book.get("author_name", ["Unknown author"])
    author = ", ".join(authors)

    year = book.get("first_publish_year", "Unknown year")

    print(f"- {title}")
    print(f"  Author: {author}")
    print(f"  First published: {year}")