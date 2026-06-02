from __future__ import annotations

import asyncio
import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.ai.nutrition.food_lookup import FoodLookupService
from app.ai.nutrition.meal_parser import MealTextParser
from app.ai.nutrition.targets import NutritionTargetCalculator
from app.ai.nutrition.vision import GeminiMealVisionService
from app.db.session import get_db
from app.dependencies import get_current_user
from app.modules.nutrition.routes import router as nutrition_router
from app.modules.nutrition.schemas import MealLookupResponse
from app.modules.nutrition.service import NutritionService


class FakeUploadFile:
    filename = "meal.jpg"
    content_type = "image/jpeg"

    async def read(self) -> bytes:
        return b"image-bytes"


class FakeVision:
    async def detect_food_items(self, image_bytes: bytes, content_type: str) -> list[dict]:
        return [{"name": "chicken breast", "grams": 100}, {"name": "rice", "grams": 150}]


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
    items = MealTextParser().parse("100g chicken breast and 2 eggs, 1 cup rice")

    assert items == [
        {"name": "chicken breast", "grams": 100},
        {"name": "eggs", "grams": 100},
        {"name": "rice", "grams": 150},
    ]


def test_target_calculator_uses_mifflin_st_jeor_and_goal_modifier():
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


def test_food_lookup_fallback_returns_labeled_usda_based_values():
    result = asyncio.run(FoodLookupService(api_key=None).search("2 eggs"))

    assert result is None

    result = asyncio.run(FoodLookupService(api_key=None).search("eggs"))

    assert result["name"] == "whole egg"
    assert result["analysis_method"] == "fallback"
    assert result["protein_per_100g"] == 12.56


def test_gemini_response_validation_accepts_structured_json():
    response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": '{"items":[{"name":"Chicken Breast","grams":150},{"name":"White Rice","grams":180}]}'}
                    ]
                }
            }
        ]
    }

    assert GeminiMealVisionService.validate_response(response) == [
        {"name": "chicken breast", "grams": 150.0},
        {"name": "white rice", "grams": 180.0},
    ]


def test_image_analysis_calculates_macros_without_filename_matching(tmp_path, monkeypatch):
    monkeypatch.setattr("app.modules.nutrition.service.settings.local_upload_dir", str(tmp_path))
    service = NutritionService(db=None)
    service.vision = FakeVision()
    service.food_lookup = FakeFoodLookup()

    result = asyncio.run(service.analyze_meal_image(FakeUser(), FakeUploadFile()))

    assert result.total_calories == 360
    assert result.protein_g == 35.1
    assert result.carbs_g == 42.3
    assert result.fat_g == 4.0
    assert result.confidence == 1
    assert result.analysis_method == "gemini_usda"
    assert "meal.jpg" not in result.estimate.name.lower()


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
                explanation="Detected chicken breast cooked (100g). Nutrition values were retrieved from USDA FoodData Central.",
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
