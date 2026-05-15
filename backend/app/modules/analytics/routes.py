from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.modules.analytics.schemas import AnalyticsHistoryResponse, PredictiveAnalyticsResponse, WeeklyReportResponse
from app.modules.analytics.service import AnalyticsService
from app.modules.auth.models import User

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/predictive", response_model=PredictiveAnalyticsResponse)
def predictive_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AnalyticsService(db).predictive_summary(current_user)


@router.get("/weekly-report/latest", response_model=WeeklyReportResponse)
def latest_weekly_report(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AnalyticsService(db).latest_weekly_report(current_user)


@router.get("/history", response_model=AnalyticsHistoryResponse)
def analytics_history(days: int = 90, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AnalyticsService(db).history(current_user, days=days)
