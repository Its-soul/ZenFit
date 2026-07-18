from app.ai.config import get_ai_settings
from app.ai.predictions.features import feature_vector
from app.ai.registry import registry
from app.ai.schemas import AdherencePrediction


def risk_level(probability: float) -> str:
    return "high" if probability >= .7 else "moderate" if probability >= .4 else "low"


def predict_adherence(features: dict) -> AdherencePrediction:
    model = registry.get_adherence_model()
    if model is not None:
        probability = float(model.predict_proba([feature_vector(features)])[0][1])
        source, available = "xgboost", True
    else:
        completion = float(features.get("workout_completion_7d") or features.get("workout_completion_14d") or .5)
        missed = min(float(features.get("consecutive_missed") or 0), 4) * .09
        sleep_penalty = .1 if 0 < float(features.get("avg_sleep_3d") or 7) < 6 else 0
        fatigue = min(float(features.get("reported_fatigue") or 0) / 10, 1) * .12
        probability = .15 + (1 - max(0, min(1, completion))) * .5 + missed + sleep_penalty + fatigue
        source, available = "rule_engine", False
    probability = max(0.0, min(1.0, probability))
    return AdherencePrediction(miss_probability=round(probability, 3), risk_level=risk_level(probability), model_available=available, source=source, shadow_mode=get_ai_settings().shadow_mode)
