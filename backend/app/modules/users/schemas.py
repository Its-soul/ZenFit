from uuid import UUID

from pydantic import BaseModel, Field


class OnboardingRequest(BaseModel):
    primary_goal: str = Field(min_length=2, max_length=80)
    fitness_level: str = Field(min_length=2, max_length=40)
    preferred_training_days: int = Field(ge=1, le=7)
    preferred_unit: str = Field(default="metric", pattern="^(metric|imperial)$")
    weight_kg: float | None = Field(default=None, ge=30, le=300)
    height_cm: float | None = Field(default=None, ge=100, le=250)
    age: int | None = Field(default=None, ge=13, le=100)
    biological_sex: str | None = Field(default=None, pattern="^(male|female|other|prefer_not_to_say)$")


class UserProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    primary_goal: str | None
    fitness_level: str | None
    preferred_training_days: int
    preferred_unit: str
    weight_kg: float | None
    height_cm: float | None
    age: int | None
    biological_sex: str | None
    onboarding_complete: bool

    model_config = {"from_attributes": True}
