import hashlib
import math
from app.ai.registry import registry

VECTOR_SIZE = 1024


def embed_text(text: str) -> list[float]:
    model = registry.get_embedding_model()
    if model is not None:
        vector = model.encode([text], normalize_embeddings=True)[0].tolist()
        if len(vector) != VECTOR_SIZE:
            raise ValueError(f"Expected {VECTOR_SIZE}-dimension BGE-M3 embedding, got {len(vector)}")
        return vector
    # Deterministic 1024d offline fallback is explicitly not represented as BGE.
    vector = [0.0] * VECTOR_SIZE
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode()).digest()
        vector[int.from_bytes(digest[:4], "big") % VECTOR_SIZE] += 1 if digest[4] % 2 else -1
    norm = math.sqrt(sum(v * v for v in vector)) or 1
    return [v / norm for v in vector]
