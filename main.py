from difflib import SequenceMatcher


books = [
    "Worldly Light",
    "All the Light We Cannot See",
    "The Light We Lost",
    "Headlight",
    "Normal People",
    "Conversations with Friends",
]


def get_similarity(query, title):
    return SequenceMatcher(None, query, title).ratio()


def get_score(query, title):
    query = query.lower().strip()
    title = title.lower()

    # Exact title match
    if title == query:
        return 100

    # Title starts with what the user typed
    if title.startswith(query):
        return 80

    query_words = query.split()
    title_words = title.split()

    # All words from the search appear in the title
    if all(word in title_words for word in query_words):
        return 60

    # Part of the search appears in the title
    if query in title:
        return 40

    # Check for spelling mistakes
    similarity = get_similarity(query, title)

    if similarity >= 0.60:
        return 50 + (similarity * 30)

    return 0


def search_books(query):
    results = []

    for book in books:
        score = get_score(query, book)

        if score > 0:
            results.append((book, score))

    results.sort(key=lambda item: item[1], reverse=True)

    return results


query = input("Search for a book: ")

results = search_books(query)

if results:
    print("\nResults:")

    for book, score in results:
        print(f"- {book} ({score:.1f})")

else:
    print("\nNo books found.")