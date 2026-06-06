from __future__ import annotations

import asyncio
import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

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


class FakeStructuredVision:
    def __init__(self, analysis: dict):
        self.analysis = analysis

    async def analyze_meal(self, image_bytes: bytes, content_type: str) -> dict:
        assert image_bytes == b"image-bytes"
        assert content_type == "image/jpeg"
        return self.analysis


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

    assert result["name"] == "whole egg"
    assert result["analysis_method"] == "fallback"

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
                        {
                            "text": (
                                '{"meal_name":"chicken rice plate","foods":['
                                '{"name":"Chicken Breast","grams":150,"calories":248,"protein_g":46.5,"carbs_g":0,"fat_g":5.4},'
                                '{"name":"White Rice","grams":180,"calories":234,"protein_g":4.8,"carbs_g":50.7,"fat_g":0.5}'
                                '],"calories":482,"protein_g":51.3,"carbs_g":50.7,"fat_g":5.9,'
                                '"confidence":0.86,"needs_user_confirmation":false}'
                            )
                        }
                    ]
                }
            }
        ]
    }

    analysis = GeminiMealVisionService.validate_response(response)

    assert analysis["meal_name"] == "chicken rice plate"
    assert analysis["confidence"] == 0.86
    assert analysis["foods"][0]["name"] == "chicken breast"
    assert analysis["foods"][0]["grams"] == 150.0
    assert analysis["foods"][0]["calories"] == 248.0
    assert analysis["foods"][1]["name"] == "white rice"
    assert analysis["foods"][1]["grams"] == 180.0


def test_gemini_response_validation_accepts_legacy_items_json():
    response = {"items": [{"name": "Pizza", "grams": 180}]}

    analysis = GeminiMealVisionService.validate_response(response)

    assert analysis["meal_name"] == "pizza"
    assert analysis["foods"] == [{"name": "pizza", "grams": 180.0}]


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


@pytest.mark.parametrize(
    ("meal_name", "foods"),
    [
        ("pizza slice", [{"name": "pizza", "grams": 180}]),
        ("burger meal", [{"name": "burger", "grams": 220}, {"name": "french fries", "grams": 90}]),
        ("fruit bowl", [{"name": "mixed fruits", "grams": 250}]),
        ("indian thali", [{"name": "rice", "grams": 160}, {"name": "dal", "grams": 140}, {"name": "chapati", "grams": 60}, {"name": "sabzi", "grams": 120}]),
        ("chole bhature plate", [{"name": "chole bhature", "grams": 320}, {"name": "curd", "grams": 80}]),
        ("dosa breakfast", [{"name": "masala dosa", "grams": 180}, {"name": "chutney", "grams": 40}]),
        ("beverage", [{"name": "chai", "grams": 220}]),
    ],
)
def test_image_analysis_common_meals_do_not_return_zero(tmp_path, monkeypatch, meal_name, foods):
    monkeypatch.setattr("app.modules.nutrition.service.settings.local_upload_dir", str(tmp_path))
    service = NutritionService(db=None)
    service.food_lookup = FoodLookupService(api_key=None)
    service.vision = FakeStructuredVision(
        {
            "meal_name": meal_name,
            "foods": foods,
            "confidence": 0.72,
            "needs_user_confirmation": True,
            "warnings": ["Image portions are estimated."],
        }
    )

    result = asyncio.run(service.analyze_meal_image(FakeUser(), FakeUploadFile()))

    assert result.total_calories > 0
    assert result.carbs_g + result.protein_g + result.fat_g > 0
    assert result.detected_items
    assert result.estimate.name == meal_name.title()
    assert result.needs_user_confirmation is True


def test_image_analysis_uses_model_macros_when_food_database_misses(tmp_path, monkeypatch):
    monkeypatch.setattr("app.modules.nutrition.service.settings.local_upload_dir", str(tmp_path))
    service = NutritionService(db=None)
    service.food_lookup = FoodLookupService(api_key=None)
    service.vision = FakeStructuredVision(
        {
            "meal_name": "regional mixed plate",
            "foods": [
                {
                    "name": "unknown regional curry",
                    "grams": 180,
                    "calories": 260,
                    "protein_g": 9,
                    "carbs_g": 24,
                    "fat_g": 14,
                    "confidence": 0.48,
                }
            ],
            "confidence": 0.48,
            "needs_user_confirmation": True,
            "warnings": ["Food match is uncertain."],
        }
    )

    result = asyncio.run(service.analyze_meal_image(FakeUser(), FakeUploadFile()))

    assert result.total_calories == 260
    assert result.protein_g == 9
    assert result.detected_items[0].analysis_method == "vision_estimate"
    assert result.needs_user_confirmation is True


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
