class MemoryImportanceScorer:
    def score(self, *, text: str, metadata: dict) -> float:
        text_lower = text.lower()
        score = float(metadata.get("importance", 0.5))

        high_impact_terms = [
            "missed",
            "poor sleep",
            "low readiness",
            "fatigue",
            "adherence",
            "replanned",
            "struggle",
            "busy",
        ]
        if any(term in text_lower for term in high_impact_terms):
            score += 0.25
        if metadata.get("category") in {"adherence", "recovery", "sleep"}:
            score += 0.1
        if metadata.get("source") == "coach_conversation":
            score += 0.05

        return round(max(0.1, min(score, 1.0)), 3)

