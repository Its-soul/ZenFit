from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.nutrition.schemas import MealCreate, MealImageAnalysisResponse, MealResponse, NutritionTodayResponse
from app.modules.nutrition.service import NutritionService

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


@router.get("/today", response_model=NutritionTodayResponse)
def today(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return NutritionService(db).today(current_user)


@router.post("/meals", response_model=MealResponse)
def create_meal(payload: MealCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return NutritionService(db).create_meal(current_user, payload)


@router.post("/meal-image/analyze", response_model=MealImageAnalysisResponse)
async def analyze_meal_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await NutritionService(db).analyze_meal_image(current_user, file)
