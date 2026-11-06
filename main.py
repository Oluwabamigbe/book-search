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

def get_autocomplete_score(query, title):
    query = normalize_text(query)
    title = normalize_text(title)

    if not query or not title:
        return 0

    # Perfect beginning of title
    if title.startswith(query):
        return 100

    # Query appears elsewhere in title
    if query in title:
        return 85

    # Only compare the same-sized
    # beginning of the title
    title_prefix = title[:len(query)]

    key_similarity = keyboard_similarity(
        query,
        title_prefix
    )

    # Only keep very close keyboard mistakes
    if key_similarity >= 0.88:
        return key_similarity * 90

    return 0

def request_books(params, limit=50):
    url = "https://openlibrary.org/search.json"

    params = params.copy()

    params["fields"] = (
        "key,title,author_name,"
        "first_publish_year,edition_count"
    )

    params["limit"] = limit

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()["docs"]


def get_autocomplete_candidates(query):
    query = normalize_text(query)

    if not query:
        return []

    words = query.split()

    parts = []

    for word in words:
        part = (
            f"(title_suggest:{word}* "
            f"OR title:{word}*)"
        )

        parts.append(part)

    solr_query = " AND ".join(parts)

    return request_books(
        {"q": solr_query},
        limit=100
    )

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


def add_books_to_cache(books, cache):
    for book in books:
        key = book.get("key")

        if key:
            cache[key] = book


def autocomplete_books(query, cache):
    query = query.strip()

    if not query:
        return []

    # Try to get fresh candidates from Open Library
    if len(query) >= 2:
        try:
            fresh_books = get_autocomplete_candidates(query)

            add_books_to_cache(
                fresh_books,
                cache
            )

        except requests.RequestException:
            # If the API fails, we can still use
            # books already stored in our cache
            pass

    suggestions = []

    for book in cache.values():
        title = book.get("title", "")

        score = get_autocomplete_score(
            query,
            title
        )

        if score > 0:
            suggestions.append(
                (book, score)
            )

    suggestions.sort(
        key=lambda item: (
            -item[1],
            len(
                normalize_text(
                    item[0].get("title", "")
                )
            )
        )
    )

    return suggestions[:5]


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


book_cache = {}


while True:
    query = input(
        "\nType a title "
        "(or 'q' to stop): "
    )

    if query.lower() == "q":
        break

    suggestions = autocomplete_books(
        query,
        book_cache
    )

    if suggestions:
        print("\nSuggestions:")

        for book, score in suggestions:
            title = book.get(
                "title",
                "Unknown title"
            )

            authors = book.get(
                "author_name",
                ["Unknown author"]
            )

            author = ", ".join(authors)

            print(
                f"- {title} "
                f"by {author} "
                f"({score:.1f})"
            )

    else:
        print("\nNo suggestions found.")