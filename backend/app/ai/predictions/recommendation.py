from app.ai.registry import registry

DEFAULTS = ["maintain_original_plan", "reschedule_workout", "reduce_workout_duration", "reduce_intensity", "recovery_session", "walking_session"]


def rank_recommendations(context: dict, candidates: list[str] | None = None) -> list[dict]:
    candidates = candidates or DEFAULTS
    readiness, miss = float(context.get("readiness", 70)), float(context.get("miss_probability", .3))
    scores = {}
    for candidate in candidates:
        score = .5
        if miss >= .7 and candidate in {"reschedule_workout", "reduce_workout_duration"}: score += .3
        if readiness < 45 and candidate in {"reduce_intensity", "recovery_session", "walking_session"}: score += .35
        if readiness >= 75 and candidate == "maintain_original_plan": score += .35
        scores[candidate] = min(score, 1)
    # XGBoost feedback model is optional; deterministic ranking remains auditable.
    return [{"recommendation": k, "accept_probability": round(v, 3), "source": "rule_engine"} for k,v in sorted(scores.items(), key=lambda x:x[1], reverse=True)]
