from qdrant_client.http.models import PointStruct
from app.core.qdrant_client import USER_MEMORY_COLLECTION, get_qdrant_client
from app.zenfit_ai.config import get_ai_settings
from app.zenfit_ai.memory.embeddings import embed_text


def migrate_batch(offset=None, limit: int = 100) -> tuple[dict, object | None]:
    client = get_qdrant_client()
    records, next_offset = client.scroll(collection_name=USER_MEMORY_COLLECTION, offset=offset, limit=limit, with_payload=True)
    points = []; stats = {"scanned": len(records), "already_migrated": 0, "newly_migrated": 0, "failed": 0}
    for record in records:
        payload = dict(record.payload or {})
        text = payload.get("text", "")
        if not text:
            stats["failed"] += 1; continue
        try:
            existing = client.retrieve(collection_name=get_ai_settings().memory_collection, ids=[record.id], with_payload=False, with_vectors=False)
            if existing: stats["already_migrated"] += 1; continue
            points.append(PointStruct(id=record.id, vector=embed_text(text), payload=payload))
        except Exception:
            stats["failed"] += 1
    if points:
        client.upsert(collection_name=get_ai_settings().memory_collection, points=points, wait=True)
        stats["newly_migrated"] = len(points)
    return stats, next_offset
