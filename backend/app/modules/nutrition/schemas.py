from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MealCreate(BaseModel):
    name: str = Field(min_length=2, max_length=140)
    meal_type: str = "meal"
    calories: int = Field(ge=0, le=5000)
    protein_g: float = Field(default=0, ge=0, le=500)
    carbs_g: float = Field(default=0, ge=0, le=800)
    fat_g: float = Field(default=0, ge=0, le=400)
    logged_at: datetime | None = None
    image_path: str | None = None
    analysis_explanation: str | None = None


class MealResponse(BaseModel):
    id: UUID
    name: str
    meal_type: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    image_path: str | None = None
    analysis_explanation: str | None = None
    logged_at: datetime

    model_config = {"from_attributes": True}


class NutritionTodayResponse(BaseModel):
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    calorie_target: int
    protein_target_g: float
    targets_are_estimated: bool = False
    meals: list[MealResponse]


class DetectedFoodItem(BaseModel):
    name: str
    grams: float
    calories: int = 0
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0
    confidence: float | None = None
    analysis_method: str | None = None


class MealLookupRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)


class MealLookupResponse(BaseModel):
    detected_items: list[DetectedFoodItem]
    total_calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    confidence: float
    analysis_method: str
    explanation: str
    needs_user_confirmation: bool = False
    warnings: list[str] = Field(default_factory=list)
    estimate: MealCreate
