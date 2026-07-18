from app.ai.registry import registry
from app.ai.schemas import ReadinessPrediction


def predict_readiness(features: dict) -> ReadinessPrediction:
    factors, score = [], 75.0
    sleep = float(features.get("avg_sleep_3d") or features.get("sleep_hours") or 7)
    fatigue = float(features.get("reported_fatigue") or 0)
    soreness = float(features.get("reported_soreness") or 0)
    if sleep < 6: score -= 20; factors.append("poor_sleep")
    if fatigue >= 7: score -= 15; factors.append("high_fatigue")
    if soreness >= 7: score -= 15; factors.append("high_soreness")
    if float(features.get("days_since_rest") or 0) > 6: score -= 10; factors.append("insufficient_rest")
    model = registry.get_readiness_model()
    source = "rule_engine"
    if model is not None:
        try: score, source = float(model.predict([[sleep, fatigue, soreness]])[0]), "xgboost"
        except Exception: pass
    score = round(max(0, min(100, score)))
    level = "high" if score >= 75 else "moderate" if score >= 45 else "low"
    return ReadinessPrediction(score=score, level=level, factors=factors, source=source)
