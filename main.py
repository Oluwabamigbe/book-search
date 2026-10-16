books = [
    "Worldly Light",
    "All the Light We Cannot See",
    "The Light We Lost",
    "Headlight",
    "Normal People",
    "Conversations with Friends",
]


def search_books(query):
    query = query.lower().strip()

    exact_matches = []
    partial_matches = []

    for book in books:
        title = book.lower()

        if title == query:
            exact_matches.append(book)
        elif query in title:
            partial_matches.append(book)

    return exact_matches + partial_matches


query = input("Search for a book: ")

results = search_books(query)

if results:
    print("\nResults:")
    for book in results:
        print("-", book)
else:
    print("\nNo books found.")