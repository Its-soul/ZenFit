FEATURE_NAMES = ["workout_completion_7d", "workout_completion_14d", "workout_completion_30d", "consecutive_completed", "consecutive_missed", "days_since_last_workout", "avg_sleep_3d", "avg_sleep_7d", "latest_readiness", "avg_readiness_7d", "reported_fatigue", "reported_soreness", "scheduled_hour", "day_of_week", "weekend_flag", "historical_completion_same_day", "historical_completion_same_hour", "recent_plan_changes", "protein_target_hit_7d", "calorie_target_hit_7d"]


def feature_vector(features: dict) -> list[float]:
    result = []
    for name in FEATURE_NAMES:
        try: result.append(float(features.get(name) or 0))
        except (TypeError, ValueError): result.append(0.0)
    return result
