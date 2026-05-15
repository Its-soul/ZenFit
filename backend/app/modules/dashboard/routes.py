from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.dashboard.schemas import DashboardTodayResponse
from app.modules.dashboard.service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/today", response_model=DashboardTodayResponse)
def today(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return DashboardService(db).today(current_user)

