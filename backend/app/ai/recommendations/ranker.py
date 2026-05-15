PRIORITY_WEIGHT = {"high": 0.2, "normal": 0.1, "low": 0.0}


class RecommendationRanker:
    def rank(self, candidates: list[dict], *, context: dict) -> list[dict]:
        readiness = context.get("dashboard", {}).get("readiness_score") or 70

        def score(candidate: dict) -> float:
            base = float(candidate.get("score", 0.5))
            priority = PRIORITY_WEIGHT.get(candidate.get("priority", "normal"), 0.1)
            recovery_boost = 0.15 if readiness < 55 and candidate.get("category") == "recovery" else 0
            return base + priority + recovery_boost

        ranked = []
        for candidate in candidates:
            confidence = min(score(candidate), 0.97)
            ranked.append({**candidate, "confidence_score": round(confidence, 3)})
        return sorted(ranked, key=lambda item: item["confidence_score"], reverse=True)
