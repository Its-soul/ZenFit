from datetime import datetime, timezone
import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.nutrition.food_lookup import FoodLookupService
from app.ai.nutrition.meal_parser import MealTextParser
from app.ai.nutrition.targets import NutritionTargetCalculator
from app.events.event_types import MEAL_LOGGED
from app.events.producer import EventProducer
from app.modules.auth.models import User
from app.modules.nutrition.repository import NutritionRepository
from app.modules.nutrition.schemas import MealCreate, MealLookupResponse, NutritionTodayResponse

logger = logging.getLogger(__name__)


class NutritionService:
    def __init__(self, db: Session):
        self.db = db
        self.nutrition = NutritionRepository(db)
        self.events = EventProducer(db)
        self.food_lookup = FoodLookupService()
        self.meal_parser = MealTextParser()
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

    async def lookup_meal(self, user: User, query: str) -> MealLookupResponse:
        try:
            parsed_items = self.meal_parser.parse(query)
            if not parsed_items:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Could not parse meal query")
            return await self._analyze_items(parsed_items)
        except HTTPException:
            raise
        except Exception as exc:
            logger.warning("Meal lookup failed", extra={"user_id": str(user.id), "query": query, "error": str(exc)})
            return self._empty_analysis("Meal lookup failed before nutrition could be calculated.", warnings=[str(exc)])

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

    async def _analyze_items(
        self,
        items: list[dict],
        *,
        warnings: list[str] | None = None,
    ) -> MealLookupResponse:
        detected_items = []
        matched_items = 0
        methods = set()
        warnings = list(warnings or [])

        logger.info("Starting nutrition mapping", extra={"source": "text", "item_count": len(items)})

        for item in items:
            name = str(item.get("name", "")).strip().lower()
            grams = float(item.get("grams", 0) or 0)
            if not name or grams <= 0:
                logger.warning("Skipping invalid meal item", extra={"source": "text", "item": item})
                continue

            food = await self.food_lookup.search(name)
            if food:
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
                        "confidence": self._item_confidence(item, default=0.85 if method == "usda" else 0.7),
                        "analysis_method": method,
                    }
                )
                logger.info("Mapped food item", extra={"source": "text", "name": name, "mapped_name": food["name"], "method": method})
                continue

            detected_items.append({"name": name, "grams": round(grams, 1), "confidence": self._item_confidence(item, default=0.25), "analysis_method": "unmatched"})
            warnings.append(f"Detected {name}, but no nutrition match was available.")
            logger.warning("Meal item had no nutrition match", extra={"source": "text", "name": name, "grams": grams})

        if not detected_items:
            return self._empty_analysis("No valid food items were detected.", warnings=warnings)

        calories = sum(item.get("calories", 0) for item in detected_items)
        protein = round(sum(item.get("protein_g", 0) for item in detected_items), 1)
        carbs = round(sum(item.get("carbs_g", 0) for item in detected_items), 1)
        fat = round(sum(item.get("fat_g", 0) for item in detected_items), 1)
        confidence = round(matched_items / len(detected_items), 2)
        if calories > 0 and confidence == 0:
            confidence = 0.35
        method = self._analysis_method(methods=methods, confidence=confidence)
        needs_user_confirmation = confidence < 0.8 or bool(warnings)
        explanation = self._build_explanation(detected_items, method, warnings=warnings, needs_user_confirmation=needs_user_confirmation)
        final_meal_name = self._meal_name(detected_items)

        logger.warning(
            "Step 8: Nutrition mapping completed meal_name=%s calories=%s protein_g=%s carbs_g=%s fat_g=%s confidence=%s method=%s",
            final_meal_name,
            calories,
            protein,
            carbs,
            fat,
            confidence,
            method,
            extra={
                "source": "text",
                "meal_name": final_meal_name,
                "calories": calories,
                "protein_g": protein,
                "carbs_g": carbs,
                "fat_g": fat,
                "confidence": confidence,
                "method": method,
                "needs_user_confirmation": needs_user_confirmation,
            },
        )

        return MealLookupResponse(
            detected_items=detected_items,
            total_calories=calories,
            protein_g=protein,
            carbs_g=carbs,
            fat_g=fat,
            confidence=confidence,
            analysis_method=method,
            explanation=explanation,
            needs_user_confirmation=needs_user_confirmation,
            warnings=warnings,
            estimate=MealCreate(
                name=final_meal_name,
                meal_type="meal",
                calories=calories,
                protein_g=protein,
                carbs_g=carbs,
                fat_g=fat,
                analysis_explanation=explanation,
            ),
        )

    @staticmethod
    def _analysis_method(*, methods: set[str], confidence: float) -> str:
        if confidence == 0:
            return "fallback"
        if methods == {"usda"}:
            return "usda"
        if "fallback" in methods:
            return "text_fallback"
        return "text_partial"

    @staticmethod
    def _build_explanation(items: list[dict], method: str, *, warnings: list[str] | None = None, needs_user_confirmation: bool = False) -> str:
        matched = [item for item in items if item.get("analysis_method") != "unmatched"]
        if not matched:
            return "Food items were detected, but nutrition mapping needs review."
        item_text = ", ".join(f"{item['name']} ({item['grams']:g}g)" for item in matched)
        source_text = "USDA FoodData Central" if "fallback" not in method else "USDA FoodData Central where available, with local fallback values for unmatched API results"
        explanation = f"Detected {item_text}. Nutrition values were estimated from {source_text}."
        if needs_user_confirmation:
            explanation += " Please confirm portions before saving."
        if warnings:
            explanation += " " + " ".join(warnings[:3])
        return explanation

    @staticmethod
    def _meal_name(items: list[dict], fallback: str | None = None) -> str:
        names = [item["name"] for item in items if item.get("analysis_method") != "unmatched"]
        if fallback and fallback.strip():
            return fallback.strip().title()
        if not names:
            detected_names = [item["name"] for item in items if item.get("name")]
            if detected_names:
                return f"{detected_names[0].title()} Meal"
            return "Meal Needs Review"
        if len(names) == 1:
            return names[0].title()
        return f"{names[0].title()} meal"

    @staticmethod
    def _empty_analysis(explanation: str, *, warnings: list[str] | None = None) -> MealLookupResponse:
        warnings = list(warnings or [])
        return MealLookupResponse(
            detected_items=[],
            total_calories=0,
            protein_g=0,
            carbs_g=0,
            fat_g=0,
            confidence=0,
            analysis_method="fallback",
            explanation=explanation,
            needs_user_confirmation=True,
            warnings=warnings,
            estimate=MealCreate(name="Meal Needs Review", meal_type="meal", calories=0, protein_g=0, carbs_g=0, fat_g=0, analysis_explanation=explanation),
        )

    @staticmethod
    def _item_confidence(item: dict, *, default: float) -> float:
        try:
            value = float(item.get("confidence", default))
        except (TypeError, ValueError):
            value = default
        return round(max(0, min(1, value)), 2)
