from datetime import datetime, timezone

from app.ai.memory.decay import MemoryDecay


class MemoryReranker:
    def __init__(self):
        self.decay = MemoryDecay()

    def rerank(self, memories: list[dict]) -> list[dict]:
        def score(memory: dict) -> float:
            semantic_score = float(memory.get("score", 0))
            importance = self.decay.decayed_importance(memory)
            metadata = memory.get("metadata", {})
            recency = self._recency_score(metadata.get("created_at"))
            return semantic_score * 0.65 + importance * 0.2 + recency * 0.15

        ranked = sorted(memories, key=score, reverse=True)
        for memory in ranked:
            memory["rerank_score"] = round(score(memory), 4)
        return ranked

    def _recency_score(self, created_at: str | None) -> float:
        if not created_at:
            return 0.3
        try:
            timestamp = datetime.fromisoformat(created_at)
        except ValueError:
            return 0.3

        age_days = max((datetime.now(timezone.utc) - timestamp).days, 0)
        if age_days <= 1:
            return 1.0
        if age_days <= 7:
            return 0.7
        if age_days <= 30:
            return 0.45
        return 0.2
