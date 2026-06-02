import mimetypes
import uuid
from datetime import datetime, timezone
from pathlib import Path
import logging

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.ai.nutrition.food_lookup import FoodLookupService
from app.ai.nutrition.meal_parser import MealTextParser
from app.ai.nutrition.targets import NutritionTargetCalculator
from app.ai.nutrition.vision import GeminiMealVisionService
from app.events.event_types import MEAL_LOGGED
from app.events.producer import EventProducer
from app.config import settings
from app.modules.auth.models import User
from app.modules.nutrition.repository import NutritionRepository
from app.modules.nutrition.schemas import MealCreate, MealImageAnalysisResponse, MealLookupResponse, NutritionTodayResponse

logger = logging.getLogger(__name__)


class NutritionService:
    def __init__(self, db: Session):
        self.db = db
        self.nutrition = NutritionRepository(db)
        self.events = EventProducer(db)
        self.food_lookup = FoodLookupService()
        self.meal_parser = MealTextParser()
        self.vision = GeminiMealVisionService()
        self.targets = NutritionTargetCalculator()

    def create_meal(self, user: User, payload: MealCreate):
        self._validate_logged_at(payload.logged_at)
        meal = self.nutrition.create_meal(user.id, payload)
        self.events.emit(
            user_id=user.id,
            event_type=MEAL_LOGGED,
            payload={"meal_id": str(meal.id), "calories": meal.calories, "protein_g": meal.protein_g, "meal_type": meal.meal_type},
        )
        self.db.commit()
        self.db.refresh(meal)
        return meal

    async def analyze_meal_image(self, user: User, file: UploadFile) -> MealImageAnalysisResponse:
        content_type = file.content_type or mimetypes.guess_type(file.filename or "")[0] or ""
        if not content_type.startswith("image/"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Upload an image file")

        extension = Path(file.filename or "meal.jpg").suffix.lower() or ".jpg"
        if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supported image types are JPG, PNG, and WebP")

        upload_dir = Path(settings.local_upload_dir) / "meals" / str(user.id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_name = f"{uuid.uuid4()}{extension}"
        destination = upload_dir / file_name
        content = await file.read()
        if len(content) > 6 * 1024 * 1024:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Meal images must be under 6MB")
        destination.write_bytes(content)

        image_path = str(destination).replace("\\", "/")
        try:
            detected_items = await self.vision.detect_food_items(content, content_type)
            analysis = await self._analyze_items(detected_items, source="image")
        except Exception as exc:
            logger.warning("Meal image analysis failed", extra={"user_id": str(user.id), "error": str(exc)})
            analysis = self._empty_analysis("Image analysis failed before nutrition could be calculated.")

        analysis.estimate.image_path = image_path
        analysis.estimate.analysis_explanation = analysis.explanation
        return MealImageAnalysisResponse(
            **analysis.model_dump(),
            upload_url=f"/uploads/meals/{user.id}/{file_name}",
            image_path=image_path,
        )

    async def lookup_meal(self, user: User, query: str) -> MealLookupResponse:
        try:
            parsed_items = self.meal_parser.parse(query)
            if not parsed_items:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Could not parse meal query")
            return await self._analyze_items(parsed_items, source="text")
        except HTTPException:
            raise
        except Exception as exc:
            logger.warning("Meal lookup failed", extra={"user_id": str(user.id), "query": query, "error": str(exc)})
            return self._empty_analysis("Meal lookup failed before nutrition could be calculated.")

    def today(self, user: User) -> NutritionTodayResponse:
        meals = self.nutrition.list_today(user.id)
        calories = sum(meal.calories for meal in meals)
        protein = sum(meal.protein_g for meal in meals)
        carbs = sum(meal.carbs_g for meal in meals)
        fat = sum(meal.fat_g for meal in meals)
        profile = getattr(user, "profile", None)
        targets = self.targets.calculate(
            weight_kg=getattr(profile, "weight_kg", None),
            height_cm=getattr(profile, "height_cm", None),
            age=getattr(profile, "age", None),
            biological_sex=getattr(profile, "biological_sex", None),
            training_frequency=getattr(profile, "preferred_training_days", None),
            goal=getattr(profile, "primary_goal", None),
        )
        return NutritionTodayResponse(
            calories=calories,
            protein_g=protein,
            carbs_g=carbs,
            fat_g=fat,
            calorie_target=targets["calorie_target"],
            protein_target_g=targets["protein_target_g"],
            targets_are_estimated=targets["targets_are_estimated"],
            meals=meals,
        )

    def _validate_logged_at(self, logged_at: datetime | None) -> None:
        if logged_at and logged_at.tzinfo is None:
            logged_at = logged_at.replace(tzinfo=timezone.utc)
        if logged_at and logged_at > datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Meal logs cannot be created in the future")

    async def _analyze_items(self, items: list[dict], *, source: str) -> MealLookupResponse:
        detected_items = []
        matched_items = 0
        methods = set()

        for item in items:
            name = str(item.get("name", "")).strip().lower()
            grams = float(item.get("grams", 0) or 0)
            if not name or grams <= 0:
                continue

            food = await self.food_lookup.search(name)
            if not food:
                detected_items.append({"name": name, "grams": round(grams, 1), "analysis_method": "unmatched"})
                continue

            matched_items += 1
            method = food.get("analysis_method", "usda")
            methods.add(method)
            factor = grams / 100
            detected_items.append(
                {
                    "name": food["name"],
                    "grams": round(grams, 1),
                    "calories": round(food["calories_per_100g"] * factor),
                    "protein_g": round(food["protein_per_100g"] * factor, 1),
                    "carbs_g": round(food["carbs_per_100g"] * factor, 1),
                    "fat_g": round(food["fat_per_100g"] * factor, 1),
                    "analysis_method": method,
                }
            )

        if not detected_items:
            return self._empty_analysis("No valid food items were detected.")

        calories = sum(item.get("calories", 0) for item in detected_items)
        protein = round(sum(item.get("protein_g", 0) for item in detected_items), 1)
        carbs = round(sum(item.get("carbs_g", 0) for item in detected_items), 1)
        fat = round(sum(item.get("fat_g", 0) for item in detected_items), 1)
        confidence = round(matched_items / len(detected_items), 2)
        method = self._analysis_method(source=source, methods=methods, confidence=confidence)
        explanation = self._build_explanation(detected_items, method)
        meal_name = self._meal_name(detected_items)

        return MealLookupResponse(
            detected_items=detected_items,
            total_calories=calories,
            protein_g=protein,
            carbs_g=carbs,
            fat_g=fat,
            confidence=confidence,
            analysis_method=method,
            explanation=explanation,
            estimate=MealCreate(
                name=meal_name,
                meal_type="meal",
                calories=calories,
                protein_g=protein,
                carbs_g=carbs,
                fat_g=fat,
                analysis_explanation=explanation,
            ),
        )

    @staticmethod
    def _analysis_method(*, source: str, methods: set[str], confidence: float) -> str:
        if confidence == 0:
            return "fallback"
        if methods == {"usda"}:
            return "gemini_usda" if source == "image" else "usda"
        if "fallback" in methods:
            return f"{source}_fallback"
        return f"{source}_partial"

    @staticmethod
    def _build_explanation(items: list[dict], method: str) -> str:
        matched = [item for item in items if item.get("analysis_method") != "unmatched"]
        if not matched:
            return "Food items were detected, but no USDA or fallback nutrition match was available."
        item_text = ", ".join(f"{item['name']} ({item['grams']:g}g)" for item in matched)
        source_text = "USDA FoodData Central" if "fallback" not in method else "USDA FoodData Central where available, with local USDA-based fallback values for unmatched API results"
        return f"Detected {item_text}. Nutrition values were retrieved from {source_text}."

    @staticmethod
    def _meal_name(items: list[dict]) -> str:
        names = [item["name"] for item in items if item.get("analysis_method") != "unmatched"]
        if not names:
            return "Unmatched meal"
        if len(names) == 1:
            return names[0].title()
        return f"{names[0].title()} meal"

    @staticmethod
    def _empty_analysis(explanation: str) -> MealLookupResponse:
        return MealLookupResponse(
            detected_items=[],
            total_calories=0,
            protein_g=0,
            carbs_g=0,
            fat_g=0,
            confidence=0,
            analysis_method="fallback",
            explanation=explanation,
            estimate=MealCreate(name="Unmatched meal", meal_type="meal", calories=0, protein_g=0, carbs_g=0, fat_g=0, analysis_explanation=explanation),
        )
