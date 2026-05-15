def chunk_text(text: str, max_words: int = 80) -> list[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text]

    chunks = []
    for index in range(0, len(words), max_words):
        chunks.append(" ".join(words[index : index + max_words]))
    return chunks

