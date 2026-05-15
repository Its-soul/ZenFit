from uuid import uuid4

from qdrant_client.http.models import FieldCondition, Filter, MatchValue, PointStruct

from app.ai.memory.embeddings import embed_text
from app.core.qdrant_client import USER_MEMORY_COLLECTION, get_qdrant_client


class VectorStore:
    def __init__(self):
        self.client = get_qdrant_client()

    def upsert_memory(self, *, user_id: str, text: str, metadata: dict) -> str:
        point_id = str(uuid4())
        payload = {"user_id": user_id, "text": text, **metadata}
        self.client.upsert(
            collection_name=USER_MEMORY_COLLECTION,
            points=[PointStruct(id=point_id, vector=embed_text(text), payload=payload)],
        )
        return point_id

    def search_memory(self, *, user_id: str, query: str, limit: int) -> list[dict]:
        results = self.client.search(
            collection_name=USER_MEMORY_COLLECTION,
            query_vector=embed_text(query),
            query_filter=Filter(must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]),
            limit=limit,
        )
        return [
            {
                "id": str(result.id),
                "score": result.score,
                "text": result.payload.get("text", ""),
                "metadata": {key: value for key, value in result.payload.items() if key not in {"text", "user_id"}},
            }
            for result in results
        ]

