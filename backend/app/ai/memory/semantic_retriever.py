import hashlib
from qdrant_client.http.models import FieldCondition, Filter, MatchValue, PointStruct
from app.core.qdrant_client import get_qdrant_client
from app.ai.config import get_ai_settings
from app.ai.memory.bge_embeddings import embed_text
from app.ai.memory.bge_reranker import rerank


class MemoryRetriever:
    def __init__(self, client=None):
        self.client = client or get_qdrant_client()
        self.collection = get_ai_settings().memory_collection

    def search(self, *, user_id: str, query: str, candidate_limit: int = 25, limit: int = 8, debug: bool = False) -> list[dict]:
        if not query.strip(): return []
        results = self.client.search(collection_name=self.collection, query_vector=embed_text(query),
            query_filter=Filter(must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]), limit=candidate_limit)
        candidates = [{"id": str(r.id), "text": (r.payload or {}).get("text", ""), "score": float(r.score), "metadata": {k:v for k,v in (r.payload or {}).items() if k not in {"text", "user_id"}}} for r in results]
        ranked = rerank(query, candidates, limit)
        if not debug:
            for item in ranked:
                item.pop("score", None); item.pop("rerank_score", None)
        return ranked

    def write(self, *, user_id: str, text: str, metadata: dict | None = None, duplicate_threshold: float = .94) -> str | None:
        if not is_durable_memory(text): return None
        existing = self.search(user_id=user_id, query=text, candidate_limit=3, limit=3, debug=True)
        if any(item.get("score", 0) >= duplicate_threshold for item in existing): return None
        point_id = hashlib.sha256(f"{user_id}:{text.strip().lower()}".encode()).hexdigest()[:32]
        self.client.upsert(collection_name=self.collection, points=[PointStruct(id=point_id, vector=embed_text(text), payload={"user_id": user_id, "text": text, **(metadata or {})})])
        return point_id


def is_durable_memory(text: str) -> bool:
    words = text.strip().lower().split()
    if len(words) < 5 or text.strip().lower() in {"hello", "thanks", "thank you"}: return False
    signals = {"prefer", "consistently", "usually", "goal", "schedule", "conflict", "sleep", "workout", "diet", "allergy", "missed", "completed"}
    return bool(signals.intersection(words))
