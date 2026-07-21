from app.ai.registry import registry
from app.ai.safety.rules import evaluate_safety
from app.core.qdrant_client import qdrant_health
from app.ai.config import get_ai_settings
from app.ai.meal_scan.artifact_loader import artifact_capability


class ZenFitAIService:
    def health(self) -> dict:
        raw = registry.status()
        classifier = artifact_capability(get_ai_settings())
        try: qdrant = qdrant_health()
        except Exception: qdrant = False
        if classifier["available"]: overall = "ready"
        else: overall = "unavailable"
        return {
            "heavy_models_enabled": raw["heavy_models_enabled"],
            "memory": {"embeddings": "ready" if raw["bge_embeddings"] else "unavailable", "reranker": "ready" if raw["bge_reranker"] else "unavailable", "qdrant": "ready" if qdrant else "unavailable"},
            "prediction": {"adherence": "ready" if raw["adherence_model"] else "fallback", "readiness": "ready" if raw["readiness_model"] else "fallback", "recommendation": "ready" if raw["recommendation_model"] else "fallback"},
            "meal_scan": {"meal_classifier": classifier, "foodsam": {"status":"ready" if raw["foodsam"] else "unavailable"}, "foodseg": {"status":"ready" if raw["foodseg103"] else "optional"}, "indian_classifier": {"status":"ready" if classifier["available"] else "unavailable","version":classifier["model_version"]}, "usda": {"status":"ready" if raw["usda_configured"] else "unavailable"}, "overall": overall},
            "pose": {"backend_analysis": "ready"},
        }

    def safety_check(self, text: str):
        return evaluate_safety(text)
