class PersonalizationEngine:
    def build_profile(self, *, patterns: dict, memories: list[dict]) -> dict:
        preferred_days = [item["value"] for item in patterns.get("preferred_workout_days", [])]
        common_meal_hours = [item["value"] for item in patterns.get("common_meal_hours", [])]

        fatigue_triggers = []
        sleep_quality = patterns.get("average_sleep_quality")
        if sleep_quality is not None and sleep_quality < 65:
            fatigue_triggers.append("low_sleep_quality")
        if patterns.get("fatigue_trend") == "rising":
            fatigue_triggers.append("rising_fatigue_checkins")

        memory_text = " ".join(memory.get("text", "").lower() for memory in memories[:10])
        motivation_triggers = patterns.get("motivation_triggers", [])
        if "busy" in memory_text:
            motivation_triggers.append("short_minimum_sessions")
        if "missed" in memory_text:
            motivation_triggers.append("replanning_explanations")

        return {
            "preferred_workout_days": preferred_days,
            "common_meal_hours": common_meal_hours,
            "fatigue_triggers": sorted(set(fatigue_triggers)),
            "motivation_triggers": sorted(set(motivation_triggers)),
            "coaching_style": self._coaching_style(patterns),
        }

    def _coaching_style(self, patterns: dict) -> str:
        if patterns.get("missed_workout_count", 0) >= 3:
            return "supportive_small_steps"
        if patterns.get("workout_completion_rate", 0) > 0.75:
            return "progression_focused"
        return "balanced_guidance"

