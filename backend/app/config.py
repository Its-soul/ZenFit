from functools import lru_cache
from pathlib import Path
import re

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent


class Settings(BaseSettings):
    app_name: str = "ZenFit"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    backend_cors_origins: str = "http://localhost:3000"
    backend_cors_origin_regex: str | None = None

    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = Field(default=None, repr=False)

    jwt_secret_key: str = Field(
        repr=False,
        validation_alias=AliasChoices("JWT_SECRET_KEY", "JWT_SECRET", "SECRET_KEY"),
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 10080
    password_reset_token_expire_minutes: int = 30
    password_reset_return_token: bool = False

    local_upload_dir: str = "uploads"
    usda_api_key: str | None = Field(default=None, repr=False, validation_alias=AliasChoices("USDA_FDC_API_KEY", "USDA_API_KEY"))
    device: str = Field(default="cpu", validation_alias="AI_DEVICE")
    model_cache_dir: Path = Field(default=REPO_ROOT / "data" / "models", validation_alias="AI_MODEL_CACHE_DIR")
    embedding_model: str = Field(default="BAAI/bge-m3", validation_alias="BGE_EMBEDDING_MODEL")
    reranker_model: str = Field(default="BAAI/bge-reranker-v2-m3", validation_alias="BGE_RERANKER_MODEL")
    memory_collection: str = Field(default="user_memory_v2", validation_alias="QDRANT_MEMORY_COLLECTION")
    adherence_model_path: Path = Field(default=REPO_ROOT / "data" / "models" / "adherence.json", validation_alias="ADHERENCE_MODEL_PATH")
    readiness_model_path: Path = Field(default=REPO_ROOT / "data" / "models" / "readiness.json", validation_alias="READINESS_MODEL_PATH")
    recommendation_model_path: Path = Field(default=REPO_ROOT / "data" / "models" / "recommendation.json", validation_alias="RECOMMENDATION_MODEL_PATH")
    indian_food_model_path: Path = Field(default=REPO_ROOT / "data" / "models" / "indian_food.pt", validation_alias="INDIAN_FOOD_MODEL_PATH")
    indian_food_classes_path: Path = Field(default=REPO_ROOT / "data" / "models" / "indian_food_classes.json", validation_alias="INDIAN_FOOD_CLASSES_PATH")
    foodsam_model_dir: Path = Field(default=REPO_ROOT / "data" / "models" / "foodsam", validation_alias="FOODSAM_MODEL_DIR")
    foodseg_model_dir: Path = Field(default=REPO_ROOT / "data" / "models" / "foodseg103", validation_alias="FOODSEG103_MODEL_DIR")
    meal_upload_dir: Path = Field(default=REPO_ROOT / "data" / "uploads" / "meals", validation_alias="MEAL_UPLOAD_DIR")
    max_meal_image_mb: int = Field(default=10, validation_alias="MAX_MEAL_IMAGE_MB")
    shadow_mode: bool = Field(default=True, validation_alias="AI_SHADOW_MODE")
    heavy_models_enabled: bool = Field(default=False, validation_alias="AI_HEAVY_MODELS_ENABLED")
    prewarm_models: str = Field(default="false", validation_alias="AI_PREWARM_MODELS")
    meal_classifier_enabled: bool = Field(default=False, validation_alias="AI_MEAL_CLASSIFIER_ENABLED")
    meal_classifier_version: str | None = Field(default=None, validation_alias="AI_MEAL_CLASSIFIER_VERSION")
    meal_classifier_environment: str = Field(default="developer-beta", validation_alias="AI_MEAL_CLASSIFIER_ENVIRONMENT")
    meal_classifier_artifact_prefix: str = Field(default="meal-classifier", validation_alias="AI_MEAL_CLASSIFIER_ARTIFACT_PREFIX")
    artifact_storage_backend: str = Field(default="local", validation_alias="AI_ARTIFACT_STORAGE_BACKEND")
    artifact_local_dir: Path = Field(default=REPO_ROOT / "data" / "artifacts", validation_alias="AI_ARTIFACT_LOCAL_DIR")
    artifact_s3_bucket: str | None = Field(default=None, validation_alias="AI_ARTIFACT_S3_BUCKET")
    artifact_s3_endpoint: str | None = Field(default=None, validation_alias="AI_ARTIFACT_S3_ENDPOINT")
    meal_classifier_high_confidence: float = Field(default=.80, validation_alias="MEAL_CLASSIFIER_HIGH_CONFIDENCE")
    meal_classifier_min_confidence: float = Field(default=.55, validation_alias="MEAL_CLASSIFIER_MIN_CONFIDENCE")

    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=("settings_",),
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, value: str) -> str:
        weak_values = {"", "change-this-" + "in-production", "secret", "jwt-secret", "dev-secret"}
        stripped_value = value.strip()
        if (
            stripped_value in weak_values
            or stripped_value.startswith("replace-with")
            or stripped_value.startswith("<")
            or len(stripped_value) < 32
        ):
            raise ValueError("JWT_SECRET_KEY must be a unique secret with at least 32 characters")
        return value

    @field_validator("meal_classifier_environment")
    @classmethod
    def validate_meal_classifier_environment(cls, value: str) -> str:
        if value not in {"developer-beta", "production"}:
            raise ValueError("AI_MEAL_CLASSIFIER_ENVIRONMENT must be developer-beta or production")
        return value

    @field_validator("meal_classifier_version")
    @classmethod
    def validate_meal_classifier_version(cls, value: str | None) -> str | None:
        if value is not None and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", value):
            raise ValueError("AI_MEAL_CLASSIFIER_VERSION contains unsupported characters")
        return value

    @field_validator("meal_classifier_artifact_prefix")
    @classmethod
    def validate_meal_classifier_artifact_prefix(cls, value: str) -> str:
        stripped = value.strip("/")
        if not stripped or ".." in stripped.split("/"):
            raise ValueError("AI_MEAL_CLASSIFIER_ARTIFACT_PREFIX is invalid")
        return stripped

    @field_validator(
        "model_cache_dir",
        "adherence_model_path",
        "readiness_model_path",
        "recommendation_model_path",
        "indian_food_model_path",
        "indian_food_classes_path",
        "foodsam_model_dir",
        "foodseg_model_dir",
        "meal_upload_dir",
        "artifact_local_dir",
        mode="after",
    )
    @classmethod
    def resolve_project_path(cls, value: Path) -> Path:
        return value if value.is_absolute() else REPO_ROOT / value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
