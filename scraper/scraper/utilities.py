def map_polish_chars(self, words: list[str]) -> list[str]:
    CHARS = {
        "\u00f3": "o", 
        "\u0142": "l",
        "\u0105": "a",
        "\u0107": "c",
        "\u0119": "e",
        "\u0144": "n",
        "\u015b": "s",
        "\u017a": "z",
        "\u017c": "z",
    }
    updated_words = list()
    for word in words:
        for polish, replacement in CHARS.items():
            if polish in word:
                word = word.replace(polish, replacement) 
        updated_words.append(word)
    return updated_words