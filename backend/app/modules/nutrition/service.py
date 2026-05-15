import mimetypes
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.events.event_types import MEAL_LOGGED
from app.events.producer import EventProducer
from app.config import settings
from app.modules.auth.models import User
from app.modules.nutrition.repository import NutritionRepository
from app.modules.nutrition.schemas import MealCreate, MealImageAnalysisResponse, NutritionTodayResponse


class NutritionService:
    def __init__(self, db: Session):
        self.db = db
        self.nutrition = NutritionRepository(db)
        self.events = EventProducer(db)

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

        estimate = self._estimate_meal_from_filename(file.filename or "meal")
        image_path = str(destination).replace("\\", "/")
        estimate.image_path = image_path
        estimate.analysis_explanation = (
            "Local demo analysis uses filename and meal-type heuristics. Review the estimate before saving."
        )
        return MealImageAnalysisResponse(
            upload_url=f"/uploads/meals/{user.id}/{file_name}",
            image_path=image_path,
            estimate=estimate,
            confidence=0.58,
            explanation=estimate.analysis_explanation,
        )

    def today(self, user: User) -> NutritionTodayResponse:
        meals = self.nutrition.list_today(user.id)
        calories = sum(meal.calories for meal in meals)
        protein = sum(meal.protein_g for meal in meals)
        carbs = sum(meal.carbs_g for meal in meals)
        fat = sum(meal.fat_g for meal in meals)
        return NutritionTodayResponse(
            calories=calories,
            protein_g=protein,
            carbs_g=carbs,
            fat_g=fat,
            calorie_target=2200,
            protein_target_g=150,
            meals=meals,
        )

    def _validate_logged_at(self, logged_at: datetime | None) -> None:
        if logged_at and logged_at.tzinfo is None:
            logged_at = logged_at.replace(tzinfo=timezone.utc)
        if logged_at and logged_at > datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Meal logs cannot be created in the future")

    def _estimate_meal_from_filename(self, filename: str) -> MealCreate:
        name = Path(filename).stem.replace("_", " ").replace("-", " ").strip() or "Uploaded meal"
        lower_name = name.lower()
        if any(word in lower_name for word in ["salad", "bowl", "chicken", "rice"]):
            return MealCreate(name=name.title(), meal_type="meal", calories=520, protein_g=38, carbs_g=52, fat_g=18)
        if any(word in lower_name for word in ["shake", "smoothie", "yogurt"]):
            return MealCreate(name=name.title(), meal_type="snack", calories=340, protein_g=28, carbs_g=42, fat_g=7)
        if any(word in lower_name for word in ["pizza", "burger", "fries"]):
            return MealCreate(name=name.title(), meal_type="meal", calories=820, protein_g=32, carbs_g=86, fat_g=38)
        return MealCreate(name=name.title(), meal_type="meal", calories=610, protein_g=31, carbs_g=64, fat_g=22)
