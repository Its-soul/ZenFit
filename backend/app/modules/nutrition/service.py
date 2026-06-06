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
from app.ai.nutrition.vision import GeminiMealVisionService, MealVisionConfigurationError, MealVisionError, MealVisionProviderError
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
        content_type = (file.content_type or mimetypes.guess_type(file.filename or "")[0] or "").lower()
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
        if not content:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded image is empty")
        if len(content) > 6 * 1024 * 1024:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Meal images must be under 6MB")
        destination.write_bytes(content)

        image_path = str(destination).replace("\\", "/")
        logger.warning(
            "Step 1: Image received user_id=%s filename=%s content_type=%s",
            str(user.id),
            file.filename,
            content_type,
        )
        logger.warning(
            "Step 2: Image size bytes=%s saved_path=%s",
            len(content),
            image_path,
        )
        logger.info(
            "Meal image uploaded user_id=%s filename=%s content_type=%s bytes=%s image_path=%s",
            str(user.id),
            file.filename,
            content_type,
            len(content),
            image_path,
            extra={
                "user_id": str(user.id),
                "filename": file.filename,
                "content_type": content_type,
                "bytes": len(content),
                "image_path": image_path,
            },
        )
        try:
            vision_analysis = await self._detect_meal_from_image(content, content_type)
            analysis = await self._analyze_items(
                vision_analysis["foods"],
                source="image",
                meal_name=vision_analysis.get("meal_name"),
                vision_totals=vision_analysis,
                vision_confidence=vision_analysis.get("confidence"),
                warnings=vision_analysis.get("warnings") or [],
            )
        except MealVisionConfigurationError as exc:
            logger.error("Meal image analysis is not configured", extra={"user_id": str(user.id), "error": str(exc)})
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
        except MealVisionProviderError as exc:
            logger.error(
                "Meal image provider error user_id=%s status_code=%s detail=%s",
                str(user.id),
                exc.status_code,
                str(exc),
            )
            raise HTTPException(status_code=self._provider_http_status(exc), detail=str(exc)) from exc
        except MealVisionError as exc:
            logger.warning("Meal image analysis failed", extra={"user_id": str(user.id), "error": str(exc)})
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

        analysis.estimate.image_path = image_path
        analysis.estimate.analysis_explanation = analysis.explanation
        logger.warning(
            "Step 8: Final JSON meal_name=%s calories=%s protein_g=%s carbs_g=%s fat_g=%s confidence=%s",
            analysis.estimate.name,
            analysis.total_calories,
            analysis.protein_g,
            analysis.carbs_g,
            analysis.fat_g,
            analysis.confidence,
        )
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
            return self._empty_analysis("Meal lookup failed before nutrition could be calculated.", warnings=[str(exc)])

    async def _detect_meal_from_image(self, content: bytes, content_type: str) -> dict:
        if hasattr(self.vision, "analyze_meal"):
            return await self.vision.analyze_meal(content, content_type)
        foods = await self.vision.detect_food_items(content, content_type)
        return {
            "meal_name": self._meal_name(foods),
            "foods": foods,
            "confidence": 1.0,
            "needs_user_confirmation": True,
            "warnings": ["Vision service returned item-only output."],
        }

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
        source: str,
        meal_name: str | None = None,
        vision_totals: dict | None = None,
        vision_confidence: float | None = None,
        warnings: list[str] | None = None,
    ) -> MealLookupResponse:
        detected_items = []
        matched_items = 0
        methods = set()
        warnings = list(warnings or [])

        logger.warning("Step 7: Nutrition lookup starting source=%s item_count=%s meal_name=%s", source, len(items), meal_name)
        logger.info("Starting nutrition mapping", extra={"source": source, "item_count": len(items), "meal_name": meal_name})

        for item in items:
            name = str(item.get("name", "")).strip().lower()
            grams = float(item.get("grams", 0) or 0)
            if not name or grams <= 0:
                logger.warning("Skipping invalid detected food item", extra={"source": source, "item": item})
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
                logger.info("Mapped food item", extra={"source": source, "name": name, "mapped_name": food["name"], "method": method})
                continue

            model_estimate = self._model_estimated_food(item)
            if model_estimate:
                matched_items += 1
                methods.add("vision_estimate")
                detected_items.append(model_estimate)
                warnings.append(f"Used model-estimated nutrition for {name}; confirm the values.")
                logger.info("Used model-estimated nutrition item", extra={"source": source, "name": name})
                continue

            detected_items.append({"name": name, "grams": round(grams, 1), "confidence": self._item_confidence(item, default=0.25), "analysis_method": "unmatched"})
            warnings.append(f"Detected {name}, but no nutrition match was available.")
            logger.warning("Detected food item had no nutrition match", extra={"source": source, "name": name, "grams": grams})

        if not detected_items:
            return self._empty_analysis("No valid food items were detected.", warnings=warnings)

        calories = sum(item.get("calories", 0) for item in detected_items)
        protein = round(sum(item.get("protein_g", 0) for item in detected_items), 1)
        carbs = round(sum(item.get("carbs_g", 0) for item in detected_items), 1)
        fat = round(sum(item.get("fat_g", 0) for item in detected_items), 1)
        if calories == 0 and vision_totals and self._total_calories(vision_totals) > 0:
            calories = self._total_calories(vision_totals)
            protein = round(float(vision_totals.get("protein_g") or 0), 1)
            carbs = round(float(vision_totals.get("carbs_g") or 0), 1)
            fat = round(float(vision_totals.get("fat_g") or 0), 1)
            methods.add("vision_total_estimate")
            warnings.append("Used whole-meal model estimate because per-item nutrition mapping was incomplete.")

        coverage_confidence = matched_items / len(detected_items)
        if vision_confidence is not None and source == "image":
            confidence = round((coverage_confidence + max(0, min(1, float(vision_confidence)))) / 2, 2)
        else:
            confidence = round(coverage_confidence, 2)
        if calories > 0 and confidence == 0:
            confidence = 0.35
        method = self._analysis_method(source=source, methods=methods, confidence=confidence)
        needs_user_confirmation = confidence < 0.8 or bool(warnings) or "vision_estimate" in methods or "vision_total_estimate" in methods
        explanation = self._build_explanation(detected_items, method, warnings=warnings, needs_user_confirmation=needs_user_confirmation)
        final_meal_name = self._meal_name(detected_items, fallback=meal_name)

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
                "source": source,
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
    def _analysis_method(*, source: str, methods: set[str], confidence: float) -> str:
        if confidence == 0:
            return "fallback"
        if methods == {"usda"}:
            return "gemini_usda" if source == "image" else "usda"
        if "vision_total_estimate" in methods:
            return "gemini_estimate"
        if "vision_estimate" in methods:
            return "gemini_partial_estimate"
        if "fallback" in methods:
            return f"{source}_fallback"
        return f"{source}_partial"

    @staticmethod
    def _build_explanation(items: list[dict], method: str, *, warnings: list[str] | None = None, needs_user_confirmation: bool = False) -> str:
        matched = [item for item in items if item.get("analysis_method") != "unmatched"]
        if not matched:
            return "Food items were detected, but nutrition mapping needs review."
        item_text = ", ".join(f"{item['name']} ({item['grams']:g}g)" for item in matched)
        if "estimate" in method:
            source_text = "Gemini's structured meal estimate where database mapping was incomplete"
        else:
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

    def _model_estimated_food(self, item: dict) -> dict | None:
        calories = self._positive_float(item.get("calories"))
        protein = self._positive_float(item.get("protein_g"))
        carbs = self._positive_float(item.get("carbs_g"))
        fat = self._positive_float(item.get("fat_g"))
        if calories <= 0 and protein <= 0 and carbs <= 0 and fat <= 0:
            return None
        return {
            "name": str(item.get("name", "")).strip().lower(),
            "grams": round(float(item.get("grams", 0) or 0), 1),
            "calories": round(calories),
            "protein_g": round(protein, 1),
            "carbs_g": round(carbs, 1),
            "fat_g": round(fat, 1),
            "confidence": self._item_confidence(item, default=0.55),
            "analysis_method": "vision_estimate",
        }

    @staticmethod
    def _positive_float(value) -> float:
        try:
            parsed = float(value or 0)
        except (TypeError, ValueError):
            return 0
        return max(0, parsed)

    @staticmethod
    def _total_calories(vision_totals: dict) -> int:
        try:
            return round(float(vision_totals.get("calories") or 0))
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _provider_http_status(exc: MealVisionProviderError) -> int:
        if exc.status_code in {400, 415}:
            return status.HTTP_422_UNPROCESSABLE_ENTITY
        if exc.status_code in {401, 403, 404, 429, 500, 503, 504}:
            return status.HTTP_503_SERVICE_UNAVAILABLE
        return status.HTTP_503_SERVICE_UNAVAILABLE
