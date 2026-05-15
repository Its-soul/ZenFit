import hashlib
import math

VECTOR_SIZE = 384


def embed_text(text: str) -> list[float]:
    """Create a deterministic local embedding.

    This keeps development fully local. Later, this function can be swapped for
    a stronger embedding model without changing retriever or vector-store code.
    """
    vector = [0.0] * VECTOR_SIZE
    tokens = [token.strip().lower() for token in text.split() if token.strip()]

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % VECTOR_SIZE
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign

    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]

