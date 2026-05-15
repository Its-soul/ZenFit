from datetime import datetime, timezone


class MemoryDecay:
    def decayed_importance(self, memory: dict) -> float:
        metadata = memory.get("metadata", {})
        importance = float(metadata.get("importance", 0.5))
        created_at = metadata.get("created_at")
        if not created_at:
            return importance

        try:
            age_days = (datetime.now(timezone.utc) - datetime.fromisoformat(created_at)).days
        except ValueError:
            return importance

        if metadata.get("category") in {"adherence", "recovery"}:
            decay_rate = 0.004
        else:
            decay_rate = 0.008

        return round(max(0.1, importance - age_days * decay_rate), 3)

