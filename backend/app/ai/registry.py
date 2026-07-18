from functools import lru_cache
import importlib.util
import logging
from pathlib import Path

from app.ai.config import get_ai_settings

logger = logging.getLogger(__name__)
HEAVY_MODEL_KEYS={"bge_embeddings","bge_reranker","indian_food_classifier"}


class ModelRegistry:
    """Lazy, process-local model registry. Optional dependency failures are contained."""

    def __init__(self):
        self.settings = get_ai_settings()
        self._instances: dict[str, object | None] = {}
        self._errors: dict[str, str] = {}

    def _remember(self, key, loader):
        if key in HEAVY_MODEL_KEYS and not self.settings.heavy_models_enabled:
            self._errors[key] = "heavy models disabled by configuration"
            return None
        if key not in self._instances:
            try:
                self._instances[key] = loader()
                logger.info("Loaded local AI capability %s", key)
            except Exception as exc:
                self._instances[key] = None
                self._errors[key] = str(exc)
                logger.warning("AI capability %s unavailable: %s", key, exc)
        return self._instances[key]

    def _device(self) -> str:
        if self.settings.device != "auto":
            return self.settings.device
        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"

    def get_embedding_model(self):
        def load():
            from sentence_transformers import SentenceTransformer
            return SentenceTransformer(self.settings.embedding_model, device=self._device(), cache_folder=str(self.settings.model_cache_dir))
        return self._remember("bge_embeddings", load)

    def get_reranker(self):
        def load():
            from sentence_transformers import CrossEncoder
            return CrossEncoder(self.settings.reranker_model, device=self._device(), cache_dir=str(self.settings.model_cache_dir))
        return self._remember("bge_reranker", load)

    def _xgboost(self, key: str, path: Path):
        def load():
            if not path.exists():
                raise FileNotFoundError(path)
            import xgboost as xgb
            model = xgb.XGBClassifier()
            model.load_model(path)
            return model
        return self._remember(key, load)

    def get_adherence_model(self): return self._xgboost("adherence_model", self.settings.adherence_model_path)
    def get_readiness_model(self): return self._xgboost("readiness_model", self.settings.readiness_model_path)
    def get_recommendation_model(self): return self._xgboost("recommendation_model", self.settings.recommendation_model_path)

    def get_food_classifier(self):
        from app.ai.meal_scan.classifier import load_classifier
        return self._remember("indian_food_classifier", load_classifier)

    def food_classifier_version(self) -> str | None:
        active=self.settings.indian_food_model_path.parent/"indian_food"/"active.json"
        try:
            import json
            return json.loads(active.read_text()).get("version") if active.exists() else ("legacy" if self.settings.indian_food_model_path.exists() else None)
        except Exception:return None

    def status(self) -> dict[str, bool]:
        def cached(model_name: str) -> bool:
            slug="models--"+model_name.replace("/","--")
            return (self.settings.model_cache_dir/slug).exists() or (self.settings.model_cache_dir/model_name.replace("/","_")).exists()
        return {
            "heavy_models_enabled": self.settings.heavy_models_enabled,
            "bge_embeddings": self.settings.heavy_models_enabled and self.error("bge_embeddings") is None and (self.loaded("bge_embeddings") or (importlib.util.find_spec("sentence_transformers") is not None and cached(self.settings.embedding_model))),
            "bge_reranker": self.settings.heavy_models_enabled and self.error("bge_reranker") is None and (self.loaded("bge_reranker") or (importlib.util.find_spec("sentence_transformers") is not None and cached(self.settings.reranker_model))),
            "adherence_model": self.settings.adherence_model_path.exists(),
            "readiness_model": self.settings.readiness_model_path.exists(),
            "recommendation_model": self.settings.recommendation_model_path.exists(),
            "foodsam": self.settings.heavy_models_enabled and (self.settings.foodsam_model_dir/"zenfit_adapter.py").exists(),
            "foodseg103": self.settings.heavy_models_enabled and (self.settings.foodseg_model_dir/"zenfit_adapter.py").exists(),
            "indian_food_classifier": self.settings.heavy_models_enabled and self.food_classifier_version() is not None,
            "usda_configured": bool(self.settings.usda_api_key),
            "mediapipe": importlib.util.find_spec("mediapipe") is not None,
        }

    def loaded(self, key: str) -> bool:
        return self._instances.get(key) is not None

    def error(self, key: str) -> str | None:
        return self._errors.get(key)

    def prewarm(self, mode: str | None = None) -> dict[str,bool]:
        mode=(mode or self.settings.prewarm_models).lower()
        if mode not in {"false","core","all"}:raise ValueError("AI_PREWARM_MODELS must be false, core, or all")
        if mode=="false" or not self.settings.heavy_models_enabled:return {}
        result={"bge_embeddings":self.get_embedding_model() is not None,"bge_reranker":self.get_reranker() is not None}
        if mode=="all":result["indian_food_classifier"]=self.get_food_classifier() is not None
        return result


@lru_cache
def get_registry() -> ModelRegistry:
    return ModelRegistry()

registry = get_registry()
