books = [
    "Worldly Light",
    "All the Light We Cannot See",
    "The Light We Lost",
    "Headlight",
    "Normal People",
    "Conversations with Friends",
]


def get_score(query, title):
    query = query.lower().strip()
    title = title.lower()

    # Exact title match
    if title == query:
        return 100

    # Title starts with what the user typed
    if title.startswith(query):
        return 80

    # All query words appear somewhere in the title
    query_words = query.split()

    if all(word in title for word in query_words):
        return 60

    # Weak partial match
    if query in title:
        return 40

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
        print(f"- {book} ({score})")

else:
    print("\nNo books found.")