from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class RecoveryCheckinCreate(BaseModel):
    checkin_date: date
    fatigue_score: int = Field(ge=1, le=10)
    soreness_score: int = Field(ge=1, le=10)
    stress_score: int = Field(ge=1, le=10)
    notes: str | None = None


class RecoveryCheckinResponse(BaseModel):
    id: UUID
    checkin_date: date
    fatigue_score: int
    soreness_score: int
    stress_score: int
    readiness_score: int
    notes: str | None

    model_config = {"from_attributes": True}

