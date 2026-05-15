class TrendDetector:
    def detect(self, *, patterns: dict, predictions: dict) -> list[dict]:
        trends = []

        if patterns.get("fatigue_trend") == "rising":
            trends.append({"name": "Fatigue rising", "severity": "medium", "summary": "Recent fatigue check-ins are trending upward."})
        if patterns.get("readiness_trend") == "falling":
            trends.append({"name": "Readiness declining", "severity": "high", "summary": "Readiness is moving downward across recent check-ins."})
        if predictions.get("adherence_risk", {}).get("level") == "high":
            trends.append({"name": "Adherence risk high", "severity": "high", "summary": "Missed sessions and memory signals suggest consistency risk."})
        if patterns.get("meal_timing_consistency", 0) > 0.6:
            trends.append({"name": "Stable meal timing", "severity": "positive", "summary": "Meal logs show a consistent timing pattern."})

        return trends

