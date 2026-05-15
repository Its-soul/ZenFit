from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.recovery.schemas import RecoveryCheckinCreate, RecoveryCheckinResponse
from app.modules.recovery.service import RecoveryService

router = APIRouter(prefix="/recovery", tags=["recovery"])


@router.get("/readiness", response_model=RecoveryCheckinResponse | None)
def latest(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return RecoveryService(db).latest(current_user)


@router.post("/check-ins", response_model=RecoveryCheckinResponse)
def create_checkin(payload: RecoveryCheckinCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return RecoveryService(db).create(current_user, payload)

