"""Compatibility access to the canonical backend environment configuration."""

from app.config import Settings as AISettings
from app.config import get_settings as get_ai_settings

__all__ = ["AISettings", "get_ai_settings"]
