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
    "\u00d3": "O",
    "\u0141": "L",
    "\u0104": "A",
    "\u0106": "C",
    "\u0118": "E",
    "\u0143": "N",
    "\u015a": "s",
    "\u0179": "z",
    "\u017b": "z", 
}

def replace_polish_chars(words: list[str]) -> list[str]:
    updated_words = list()
    for word in words:
        for polish, replacement in CHARS.items():
            if polish in word:
                word = word.replace(polish, replacement) 
        updated_words.append(word)
    return updated_words