from load_synonyms import load_synonyms

SYNONYMS = load_synonyms()


def expand_query(query: str) -> str:
    words = query.lower().split()
    expanded_words = []
    
    for word in words:
        expanded_words.append(word)
        if word in SYNONYMS:
            expanded_words.extend(SYNONYMS[word])
    
    return " ".join(expanded_words)

