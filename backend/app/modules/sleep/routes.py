from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.sleep.schemas import SleepLogCreate, SleepLogResponse
from app.modules.sleep.service import SleepService

router = APIRouter(prefix="/sleep", tags=["sleep"])


@router.get("/logs", response_model=list[SleepLogResponse])
def list_recent(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SleepService(db).list_recent(current_user)


@router.post("/logs", response_model=SleepLogResponse)
def create_sleep_log(payload: SleepLogCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SleepService(db).create(current_user, payload)

