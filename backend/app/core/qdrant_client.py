import time

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PayloadSchemaType

from app.config import settings
from app.zenfit_ai.config import get_ai_settings

USER_MEMORY_COLLECTION = "user_memory"
DEFAULT_VECTOR_SIZE = 384
ZENFIT_AI_MEMORY_COLLECTION = "user_memory_v2"
ZENFIT_AI_VECTOR_SIZE = 1024


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
    v2_collection = get_ai_settings().memory_collection
    if v2_collection not in existing_names:
        client.create_collection(
            collection_name=v2_collection,
            vectors_config=VectorParams(size=ZENFIT_AI_VECTOR_SIZE, distance=Distance.COSINE),
        )
    try:
        client.create_payload_index(collection_name=v2_collection, field_name="user_id", field_schema=PayloadSchemaType.KEYWORD)
    except Exception:
        # Qdrant returns a harmless conflict when the index already exists.
        pass


def qdrant_health() -> bool:
    client = get_qdrant_client()
    client.get_collections()
    return True
