from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_ROOT.parent

def _path(name: str, default: str) -> Path:
    path = Path(os.getenv(name, default)).expanduser()
    if path.is_absolute(): return path
    parts = path.parts
    if parts and parts[0] == "backend":
        # Works in both a repo checkout and the Docker image where backend is /app.
        return BACKEND_ROOT.joinpath(*parts[1:])
    relative_root = REPO_ROOT if BACKEND_ROOT.name == "backend" else BACKEND_ROOT
    return relative_root / path


@dataclass(frozen=True)
class AISettings:
    app_env: str = os.getenv("APP_ENV", "development").lower()
    device: str = os.getenv("AI_DEVICE", "cpu")
    model_cache_dir: Path = _path("AI_MODEL_CACHE_DIR", "./data/models")
    embedding_model: str = os.getenv("BGE_EMBEDDING_MODEL", "BAAI/bge-m3")
    reranker_model: str = os.getenv("BGE_RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")
    memory_collection: str = os.getenv("QDRANT_MEMORY_COLLECTION", "user_memory_v2")
    adherence_model_path: Path = _path("ADHERENCE_MODEL_PATH", "./backend/app/zenfit_ai/models/adherence.json")
    readiness_model_path: Path = _path("READINESS_MODEL_PATH", "./backend/app/zenfit_ai/models/readiness.json")
    recommendation_model_path: Path = _path("RECOMMENDATION_MODEL_PATH", "./backend/app/zenfit_ai/models/recommendation.json")
    indian_food_model_path: Path = _path("INDIAN_FOOD_MODEL_PATH", "./backend/app/zenfit_ai/models/indian_food.pt")
    indian_food_classes_path: Path = _path("INDIAN_FOOD_CLASSES_PATH", "./backend/app/zenfit_ai/models/indian_food_classes.json")
    foodsam_model_dir: Path = _path("FOODSAM_MODEL_DIR", "./data/models/foodsam")
    foodseg_model_dir: Path = _path("FOODSEG103_MODEL_DIR", "./data/models/foodseg103")
    usda_api_key: str | None = os.getenv("USDA_FDC_API_KEY") or os.getenv("USDA_API_KEY")
    meal_upload_dir: Path = _path("MEAL_UPLOAD_DIR", "./data/uploads/meals")
    max_meal_image_mb: int = int(os.getenv("MAX_MEAL_IMAGE_MB", "10"))
    shadow_mode: bool = os.getenv("AI_SHADOW_MODE", "true").lower() not in {"0", "false", "no"}
    prewarm_models: str = os.getenv("AI_PREWARM_MODELS", "false").lower()
    meal_classifier_high_confidence: float = float(os.getenv("MEAL_CLASSIFIER_HIGH_CONFIDENCE", "0.80"))
    meal_classifier_min_confidence: float = float(os.getenv("MEAL_CLASSIFIER_MIN_CONFIDENCE", "0.55"))


@lru_cache
def get_ai_settings() -> AISettings:
    return AISettings()
