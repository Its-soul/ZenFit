from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ZenFit"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    backend_cors_origins: str = "http://localhost:3000"

    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"

    jwt_secret_key: str = Field(repr=False)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 10080
    password_reset_token_expire_minutes: int = 30
    password_reset_return_token: bool = False

    local_upload_dir: str = "uploads"
    usda_api_key: str | None = None
    gemini_api_key: str | None = None
    gemini_vision_model: str = "gemini-1.5-flash"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

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


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
