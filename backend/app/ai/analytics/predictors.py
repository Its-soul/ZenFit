class PredictiveAnalyticsEngine:
    def predict(self, *, patterns: dict, memories: list[dict]) -> dict:
        memory_risk = self._memory_risk(memories)
        completion_rate = patterns.get("workout_completion_rate", 0)
        missed_count = patterns.get("missed_workout_count", 0)
        sleep_quality = patterns.get("average_sleep_quality")
        readiness = patterns.get("average_readiness")
        fatigue_trend = patterns.get("fatigue_trend")
        readiness_trend = patterns.get("readiness_trend")
        meal_consistency = patterns.get("meal_timing_consistency", 0)

        adherence_risk = self._bounded(0.25 + missed_count * 0.08 + (1 - completion_rate) * 0.35 + memory_risk)
        fatigue_escalation = self._bounded(0.2 + (0.25 if fatigue_trend == "rising" else 0) + (0.2 if sleep_quality and sleep_quality < 60 else 0))
        recovery_decline = self._bounded(0.2 + (0.25 if readiness_trend == "falling" else 0) + (0.2 if readiness and readiness < 60 else 0))
        streak_break = self._bounded(adherence_risk * 0.7 + fatigue_escalation * 0.2)
        calorie_consistency = self._bounded(0.35 + meal_consistency * 0.45)
        workout_completion = self._bounded(0.35 + completion_rate * 0.45 - fatigue_escalation * 0.2)

        return {
            "adherence_risk": self._prediction(adherence_risk, "Risk of missing planned behaviors in the next 7 days."),
            "workout_completion_probability": self._prediction(workout_completion, "Probability the next scheduled workout is completed."),
            "fatigue_escalation": self._prediction(fatigue_escalation, "Risk that fatigue increases without plan adjustment."),
            "recovery_decline": self._prediction(recovery_decline, "Risk that readiness trends downward."),
            "streak_break": self._prediction(streak_break, "Risk that consistency streak breaks."),
            "calorie_adherence_consistency": self._prediction(calorie_consistency, "Likelihood meal logging and calorie consistency stay stable."),
        }

    def _prediction(self, value: float, explanation: str) -> dict:
        confidence = 0.55 + abs(value - 0.5) * 0.5
        return {
            "score": round(value, 3),
            "confidence": round(min(confidence, 0.92), 3),
            "level": self._level(value),
            "explanation": explanation,
        }

    def _level(self, value: float) -> str:
        if value >= 0.7:
            return "high"
        if value >= 0.4:
            return "medium"
        return "low"

    def _bounded(self, value: float) -> float:
        return max(0.0, min(1.0, value))

    def _memory_risk(self, memories: list[dict]) -> float:
        risk_terms = ["missed", "tired", "fatigue", "poor sleep", "low readiness", "busy", "struggle"]
        score = 0.0
        for memory in memories[:8]:
            text = memory.get("text", "").lower()
            if any(term in text for term in risk_terms):
                score += 0.04
        return min(score, 0.2)

