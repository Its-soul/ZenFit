from uuid import UUID

from pydantic import BaseModel, Field


class OnboardingRequest(BaseModel):
    primary_goal: str = Field(min_length=2, max_length=80)
    fitness_level: str = Field(min_length=2, max_length=40)
    preferred_training_days: int = Field(ge=1, le=7)
    preferred_unit: str = Field(default="metric", pattern="^(metric|imperial)$")


class UserProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    primary_goal: str | None
    fitness_level: str | None
    preferred_training_days: int
    preferred_unit: str
    onboarding_complete: bool

    model_config = {"from_attributes": True}

