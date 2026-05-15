import time

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from app.config import settings

USER_MEMORY_COLLECTION = "user_memory"
DEFAULT_VECTOR_SIZE = 384


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)


def ensure_qdrant_collections() -> None:
    client = get_qdrant_client()
    last_error: Exception | None = None
    for _ in range(12):
        try:
            collections = client.get_collections().collections
            break
        except Exception as exc:
            last_error = exc
            time.sleep(2)
    else:
        raise RuntimeError("Qdrant did not become ready") from last_error

    existing_names = {collection.name for collection in collections}
    if USER_MEMORY_COLLECTION not in existing_names:
        client.create_collection(
            collection_name=USER_MEMORY_COLLECTION,
            vectors_config=VectorParams(size=DEFAULT_VECTOR_SIZE, distance=Distance.COSINE),
        )


def qdrant_health() -> bool:
    client = get_qdrant_client()
    client.get_collections()
    return True
