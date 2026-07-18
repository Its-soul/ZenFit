from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.nutrition.schemas import MealCreate, MealImageAnalysisResponse, MealLookupRequest, MealLookupResponse, MealResponse, NutritionTodayResponse
from app.modules.nutrition.service import NutritionService
from app.zenfit_ai.config import get_ai_settings
from app.zenfit_ai.meal_scan.pipeline import MealScanPipeline
from app.zenfit_ai.meal_scan.schemas import ConfirmationRequest, MealAnalysis
from app.zenfit_ai.meal_scan.nutrition import USDANutritionClient
from app.zenfit_ai.meal_scan.storage import MealAnalysisStore
from app.zenfit_ai.meal_scan.models import MealAnalysisCorrection

router = APIRouter(prefix="/nutrition", tags=["nutrition"])
local_pipeline = MealScanPipeline()


@router.get("/today", response_model=NutritionTodayResponse)
def today(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return NutritionService(db).today(current_user)


@router.post("/meals", response_model=MealResponse)
def create_meal(payload: MealCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return NutritionService(db).create_meal(current_user, payload)


@router.post("/meals/lookup", response_model=MealLookupResponse)
async def lookup_meal(payload: MealLookupRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await NutritionService(db).lookup_meal(current_user, payload.query)


@router.post("/meals/analyze-image", response_model=MealImageAnalysisResponse)
async def analyze_meal_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await NutritionService(db).analyze_meal_image(current_user, file)


@router.post("/meal-image/analyze", response_model=MealImageAnalysisResponse)
async def analyze_meal_image_legacy(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await NutritionService(db).analyze_meal_image(current_user, file)


@router.post("/meals/analyze-image-local", response_model=MealAnalysis)
async def analyze_meal_image_local(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if (file.content_type or "").lower() not in allowed:
        raise HTTPException(status_code=415, detail="Supported image types are JPEG, PNG, and WebP")
    content = await file.read(get_ai_settings().max_meal_image_mb * 1024 * 1024 + 1)
    if not content: raise HTTPException(status_code=400, detail="Uploaded image is empty")
    if len(content) > get_ai_settings().max_meal_image_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Meal image exceeds configured size limit")
    try: result = await local_pipeline.analyze(content)
    except Exception as exc: raise HTTPException(status_code=422, detail=f"Invalid or unreadable image: {exc}") from exc
    try: MealAnalysisStore().save(user_id=str(current_user.id), analysis=result.model_dump(mode="json"))
    except Exception as exc: raise HTTPException(status_code=503, detail="Meal analysis storage is temporarily unavailable") from exc
    return result


@router.post("/meals/confirm-analysis", response_model=MealResponse)
async def confirm_meal_analysis(payload: ConfirmationRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not payload.foods: raise HTTPException(status_code=422, detail="At least one confirmed food is required")
    store=MealAnalysisStore()
    try: stored=store.get_for_user(user_id=str(current_user.id),analysis_id=str(payload.analysis_id))
    except Exception as exc: raise HTTPException(status_code=503,detail="Meal analysis confirmation is temporarily unavailable") from exc
    if stored is None: raise HTTPException(status_code=404,detail="Meal analysis expired or does not belong to this user")
    usda = USDANutritionClient(); totals = {"calories":0.0,"protein_g":0.0,"carbs_g":0.0,"fat_g":0.0}
    for food in payload.foods:
        item = await usda.lookup(food.name, food.grams)
        if item is None: raise HTTPException(status_code=422, detail=f"Nutrition data unavailable for {food.name}; enter the meal manually")
        for key in totals: totals[key] += item.get(key, 0)
    meal = MealCreate(name=", ".join(food.name for food in payload.foods)[:140], meal_type=payload.meal_type, calories=round(totals["calories"]), protein_g=round(totals["protein_g"],1), carbs_g=round(totals["carbs_g"],1), fat_g=round(totals["fat_g"],1), analysis_explanation=f"User-confirmed local analysis {payload.analysis_id}")
    db.add(MealAnalysisCorrection(user_id=current_user.id,analysis_id=payload.analysis_id,predicted_foods=stored.get("foods",[]),confirmed_foods=[food.model_dump(mode="json") for food in payload.foods],model_versions=sorted({food.get("model_version") for food in stored.get("foods",[]) if food.get("model_version")}),training_consent=payload.training_consent))
    saved=NutritionService(db).create_meal(current_user, meal); store.delete(str(payload.analysis_id)); return saved
