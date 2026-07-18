from typing import Any
from pydantic import BaseModel, Field


class MemoryRecord(BaseModel):
    id: str | None = None
    text: str = Field(min_length=2)
    metadata: dict[str, Any] = Field(default_factory=dict)
    score: float | None = None


class AdherencePrediction(BaseModel):
    miss_probability: float = Field(ge=0, le=1)
    risk_level: str
    model_available: bool
    source: str
    shadow_mode: bool = True


class ReadinessPrediction(BaseModel):
    score: int = Field(ge=0, le=100)
    level: str
    factors: list[str]
    source: str


class PoseRequest(BaseModel):
    exercise: str
    landmarks: list[dict[str, float]]
    timestamp: float | None = None


class SafetyResult(BaseModel):
    safe_to_continue: bool
    severity: str = "none"
    flags: list[str] = Field(default_factory=list)
    message: str | None = None
