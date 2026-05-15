from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class SleepLogCreate(BaseModel):
    sleep_date: date
    duration_hours: float = Field(ge=0, le=16)
    quality_score: int = Field(ge=1, le=100)
    notes: str | None = None


class SleepLogResponse(BaseModel):
    id: UUID
    sleep_date: date
    duration_hours: float
    quality_score: int
    notes: str | None

    model_config = {"from_attributes": True}

