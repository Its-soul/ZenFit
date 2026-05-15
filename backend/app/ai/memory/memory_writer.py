from datetime import datetime, timezone

from app.ai.memory.importance import MemoryImportanceScorer
from app.ai.memory.vector_store import VectorStore


class MemoryWriter:
    def __init__(self):
        self.vector_store = VectorStore()
        self.importance = MemoryImportanceScorer()

    def write(self, *, user_id: str, text: str, metadata: dict | None = None) -> str:
        metadata = metadata or {}
        metadata.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        metadata.setdefault("source", "ai_coach")
        metadata["importance"] = self.importance.score(text=text, metadata=metadata)

        duplicate = self._find_duplicate(user_id=user_id, text=text)
        if duplicate:
            return duplicate["id"]

        return self.vector_store.upsert_memory(user_id=user_id, text=text, metadata=metadata)

    def _find_duplicate(self, *, user_id: str, text: str) -> dict | None:
        try:
            matches = self.vector_store.search_memory(user_id=user_id, query=text, limit=1)
        except Exception:
            return None

        if not matches:
            return None

        best_match = matches[0]
        same_text = best_match.get("text", "").strip().lower() == text.strip().lower()
        very_close = float(best_match.get("score", 0)) > 0.985
        return best_match if same_text or very_close else None
