import re
import requests

from difflib import SequenceMatcher


keyboard_neighbors = {
    "q": "wa",
    "w": "qeasd",
    "e": "wrsdf",
    "r": "etdfg",
    "t": "ryfgh",
    "y": "tughj",
    "u": "yihjk",
    "i": "uojkl",
    "o": "ipkl",
    "p": "ol",

    "a": "qwsz",
    "s": "awedxz",
    "d": "serfcx",
    "f": "drtgvc",
    "g": "ftyhbv",
    "h": "gyujnb",
    "j": "huikmn",
    "k": "jiolm",
    "l": "kop",

    "z": "asx",
    "x": "zsdc",
    "c": "xdfv",
    "v": "cfgb",
    "b": "vghn",
    "n": "bhjm",
    "m": "njk",
}


def normalize_text(text):
    text = text.lower()

    # Remove punctuation
    text = re.sub(r"[^a-z0-9\s]", "", text)

    # Remove extra spaces
    text = " ".join(text.split())

    return text


def substitution_cost(letter1, letter2):
    if letter1 == letter2:
        return 0

    if letter2 in keyboard_neighbors.get(letter1, ""):
        return 0.25

    return 1


def keyboard_distance(word1, word2):
    rows = len(word1) + 1
    columns = len(word2) + 1

    distance = []

    for i in range(rows):
        row = []

        for j in range(columns):
            row.append(0)

        distance.append(row)

    for i in range(rows):
        distance[i][0] = i

    for j in range(columns):
        distance[0][j] = j

    for i in range(1, rows):
        for j in range(1, columns):

            delete = distance[i - 1][j] + 1
            insert = distance[i][j - 1] + 1

            replace = (
                distance[i - 1][j - 1]
                + substitution_cost(
                    word1[i - 1],
                    word2[j - 1]
                )
            )

            distance[i][j] = min(
                delete,
                insert,
                replace
            )

    return distance[-1][-1]


def keyboard_similarity(word1, word2):
    distance = keyboard_distance(word1, word2)

    longest = max(len(word1), len(word2))

    if longest == 0:
        return 1

    return 1 - (distance / longest)


def get_score(query, title):
    query = normalize_text(query)
    title = normalize_text(title)

    # Exact title match
    if query == title:
        return 100

    # Title begins exactly with the query
    if title.startswith(query):
        return 85

    query_words = query.split()
    title_words = title.split()

    # Every word typed appears in the title
    if all(word in title_words for word in query_words):
        return 75

    # Query appears somewhere inside the title
    if query in title:
        return 65

    normal_similarity = SequenceMatcher(
        None,
        query,
        title
    ).ratio()

    keyboard_score = keyboard_similarity(
        query,
        title
    )

    similarity = max(
        normal_similarity,
        keyboard_score
    )

    if similarity >= 0.60:
        return similarity * 60

    return 0


def request_books(params):
    url = "https://openlibrary.org/search.json"

    params["fields"] = (
        "key,title,author_name,"
        "first_publish_year,edition_count"
    )

    params["limit"] = 50

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()["docs"]


def get_books(query):
    # General search
    general_results = request_books({
        "q": query
    })

    # Also specifically ask Open Library
    # for books whose titles match the query
    title_results = request_books({
        "title": query
    })

    books = {}

    # Combine the two sets of results
    for book in general_results + title_results:
        key = book.get("key")

        if key:
            books[key] = book

    return list(books.values())


def search_books(query):
    books = get_books(query)

    results = []

    for book in books:
        title = book.get("title", "")

        score = get_score(query, title)

        if score > 0:
            results.append((book, score))

    results.sort(
        key=lambda item: item[1],
        reverse=True
    )

    return results


query = input("Search for a book: ")

results = search_books(query)

print("\nOur ranked results:\n")

for book, score in results[:10]:
    title = book.get("title", "Unknown title")

    authors = book.get(
        "author_name",
        ["Unknown author"]
    )

    author = ", ".join(authors)

    year = book.get(
        "first_publish_year",
        "Unknown year"
    )

    print(f"{title}")
    print(f"Author: {author}")
    print(f"Year: {year}")
    print(f"Search score: {score:.1f}")
    print()