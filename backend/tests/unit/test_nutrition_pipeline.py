from __future__ import annotations

import asyncio
import io
import uuid
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image

from app.ai.meal_scan.pipeline import MealScanPipeline
from app.ai.nutrition.food_lookup import FoodLookupService
from app.ai.nutrition.meal_parser import MealTextParser
from app.ai.nutrition.targets import NutritionTargetCalculator
from app.db.session import get_db
from app.dependencies import get_current_user
from app.modules.nutrition.routes import router as nutrition_router
from app.modules.nutrition.schemas import MealLookupResponse
from app.modules.nutrition.service import NutritionService


class FakeFoodLookup:
    async def search(self, query: str) -> dict | None:
        foods = {
            "chicken breast": {
                "name": "chicken breast cooked",
                "calories_per_100g": 165,
                "protein_per_100g": 31,
                "carbs_per_100g": 0,
                "fat_per_100g": 3.6,
                "analysis_method": "usda",
            },
            "rice": {
                "name": "white rice cooked",
                "calories_per_100g": 130,
                "protein_per_100g": 2.7,
                "carbs_per_100g": 28.2,
                "fat_per_100g": 0.3,
                "analysis_method": "usda",
            },
        }
        return foods.get(query)


class FakeNutritionRepository:
    def list_today(self, user_id):
        return []


class FakeUser:
    id = uuid.uuid4()

    class profile:
        weight_kg = 80
        height_cm = 180
        age = 32
        biological_sex = "male"
        preferred_training_days = 5
        primary_goal = "Build muscle"


def test_meal_text_parser_supports_units():
    assert MealTextParser().parse("100g chicken breast and 2 eggs, 1 cup rice") == [
        {"name": "chicken breast", "grams": 100},
        {"name": "eggs", "grams": 100},
        {"name": "rice", "grams": 150},
    ]


def test_target_calculator_uses_profile_and_goal():
    result = NutritionTargetCalculator().calculate(
        weight_kg=80,
        height_cm=180,
        age=32,
        biological_sex="male",
        training_frequency=5,
        goal="Build muscle",
    )
    assert result == {"calorie_target": 2994, "protein_target_g": 128.0, "targets_are_estimated": False}


def test_target_calculator_marks_missing_data_estimated():
    result = NutritionTargetCalculator().calculate(
        weight_kg=None,
        height_cm=None,
        age=None,
        biological_sex=None,
        training_frequency=None,
        goal="Maintain",
    )
    assert result["targets_are_estimated"] is True
    assert result["protein_target_g"] == 98.0


def test_food_lookup_fallback_is_labeled():
    result = asyncio.run(FoodLookupService(api_key=None).search("eggs"))
    assert result["name"] == "whole egg"
    assert result["analysis_method"] == "fallback"
    assert result["protein_per_100g"] == 12.56


def test_text_lookup_calculates_usda_macros():
    service = NutritionService(db=None)
    service.food_lookup = FakeFoodLookup()

    result = asyncio.run(service.lookup_meal(FakeUser(), "100g chicken breast and 1 cup rice"))

    assert result.total_calories == 360
    assert result.protein_g == 35.1
    assert result.carbs_g == 42.3
    assert result.fat_g == 4.0
    assert result.analysis_method == "usda"


def test_local_meal_scan_returns_manual_fallback_when_heavy_models_disabled(monkeypatch):
    monkeypatch.setattr(
        "app.ai.meal_scan.pipeline.get_ai_settings",
        lambda: SimpleNamespace(heavy_models_enabled=False),
    )
    image = Image.new("RGB", (16, 16), color="white")
    content = io.BytesIO()
    image.save(content, format="PNG")

    result = asyncio.run(MealScanPipeline().analyze(content.getvalue()))

    assert result.recognition_decision.value == "MODEL_UNAVAILABLE"
    assert result.foods == []
    assert "manually" in result.recognition_message.lower()
    assert result.recognition_reason_codes == ["heavy_models_disabled"]


def test_today_targets_come_from_user_profile():
    service = NutritionService(db=None)
    service.nutrition = FakeNutritionRepository()
    result = service.today(FakeUser())
    assert result.calorie_target == 2994
    assert result.protein_target_g == 128.0
    assert result.targets_are_estimated is False


def test_meal_lookup_endpoint_contract(monkeypatch):
    class FakeNutritionService:
        def __init__(self, db):
            pass

        async def lookup_meal(self, user, query):
            return MealLookupResponse(
                detected_items=[{"name": "chicken breast cooked", "grams": 100, "calories": 165, "protein_g": 31, "carbs_g": 0, "fat_g": 3.6}],
                total_calories=165,
                protein_g=31,
                carbs_g=0,
                fat_g=3.6,
                confidence=1,
                analysis_method="usda",
                explanation="Nutrition values were retrieved from USDA FoodData Central.",
                estimate={"name": "Chicken Breast Cooked", "meal_type": "meal", "calories": 165, "protein_g": 31, "carbs_g": 0, "fat_g": 3.6},
            )

    monkeypatch.setattr("app.modules.nutrition.routes.NutritionService", FakeNutritionService)
    app = FastAPI()
    app.include_router(nutrition_router, prefix="/api/v1")
    app.dependency_overrides[get_current_user] = lambda: FakeUser()
    app.dependency_overrides[get_db] = lambda: None

    response = TestClient(app).post("/api/v1/nutrition/meals/lookup", json={"query": "100g chicken breast"})

    assert response.status_code == 200
    assert response.json()["estimate"]["calories"] == 165


def test_legacy_cloud_image_routes_are_not_registered():
    paths = {route.path for route in nutrition_router.routes}
    assert "/nutrition/meals/analyze-image" not in paths
    assert "/nutrition/meal-image/analyze" not in paths
    assert "/nutrition/meals/analyze-image-local" in paths
