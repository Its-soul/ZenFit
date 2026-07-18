from pydantic import BaseModel, Field
from uuid import UUID


class FoodCandidate(BaseModel):
    name: str
    quantity: float = 1
    estimated_grams: float = Field(ge=0)
    confidence: float = Field(ge=0, le=1)
    nutrition: dict = Field(default_factory=dict)
    usda_food_id: int | None = None
    matched_description: str | None = None
    food_confidence: float = Field(default=0, ge=0, le=1)
    quantity_confidence: float = Field(default=0, ge=0, le=1)
    portion_confidence: float = Field(default=0, ge=0, le=1)
    nutrition_match_confidence: float = Field(default=0, ge=0, le=1)
    confidence_level: str = "low"
    top_candidates: list[dict] = Field(default_factory=list)
    bounding_box: list[float] | None = None
    model_version: str | None = None


class MealAnalysis(BaseModel):
    analysis_id: str
    foods: list[FoodCandidate]
    nutrition: dict[str, float]
    requires_confirmation: bool = True
    warnings: list[str] = Field(default_factory=list)


class ConfirmedFood(BaseModel):
    name: str
    quantity: float = Field(default=1, gt=0)
    grams: float = Field(gt=0, le=5000)


class ConfirmationRequest(BaseModel):
    analysis_id: UUID
    foods: list[ConfirmedFood]
    meal_type: str = "meal"
    training_consent: bool = False
