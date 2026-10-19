from difflib import SequenceMatcher


books = [
    "Worldly Light",
    "All the Light We Cannot See",
    "The Light We Lost",
    "Headlight",
    "Normal People",
    "Conversations with Friends",
]


# Keys that are physically close to each other on a QWERTY keyboard
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


def substitution_cost(letter1, letter2):
    if letter1 == letter2:
        return 0

    # Nearby keyboard mistake
    if letter2 in keyboard_neighbors.get(letter1, ""):
        return 0.25

    # Normal wrong letter
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

    # Cost of deleting letters
    for i in range(rows):
        distance[i][0] = i

    # Cost of adding letters
    for j in range(columns):
        distance[0][j] = j

    for i in range(1, rows):
        for j in range(1, columns):

            delete = distance[i - 1][j] + 1
            insert = distance[i][j - 1] + 1

            replace = (
                distance[i - 1][j - 1]
                + substitution_cost(word1[i - 1], word2[j - 1])
            )

            distance[i][j] = min(delete, insert, replace)

    return distance[-1][-1]


def keyboard_similarity(query, title):
    distance = keyboard_distance(query, title)

    longest_length = max(len(query), len(title))

    if longest_length == 0:
        return 1

    return 1 - (distance / longest_length)


def get_score(query, title):
    query = query.lower().strip()
    title = title.lower()

    # Exact title
    if query == title:
        return 100

    # Beginning of title
    if title.startswith(query):
        return 80

    # All search words appear in title
    query_words = query.split()

    if all(word in title for word in query_words):
        return 60

    # Regular fuzzy similarity
    normal_similarity = SequenceMatcher(
        None,
        query,
        title
    ).ratio()

    # Keyboard-aware similarity
    key_similarity = keyboard_similarity(query, title)

    # Use whichever understands the query better
    similarity = max(normal_similarity, key_similarity)

    if similarity >= 0.60:
        return 50 + (similarity * 30)

    return 0


def search_books(query):
    results = []

    for book in books:
        score = get_score(query, book)

        if score > 0:
            results.append((book, score))

    results.sort(
        key=lambda item: item[1],
        reverse=True
    )

    return results


query = input("Search for a book: ")

results = search_books(query)

if results:
    print("\nResults:")

    for book, score in results:
        print(f"- {book} ({score:.1f})")

else:
    print("\nNo books found.")