from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class WorkoutSessionCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    scheduled_date: date
    planned_intensity: str = "moderate"
    duration_minutes: int = Field(default=45, ge=10, le=240)
    notes: str | None = None


class WorkoutRescheduleRequest(BaseModel):
    scheduled_date: date
    reason: str | None = Field(default=None, max_length=240)


class WorkoutSessionResponse(BaseModel):
    id: UUID
    title: str
    scheduled_date: date
    status: str
    planned_intensity: str
    duration_minutes: int
    notes: str | None
    completed_at: datetime | None

    model_config = {"from_attributes": True}
