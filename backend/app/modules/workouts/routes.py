from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.workouts.schemas import WorkoutRescheduleRequest, WorkoutSessionCreate, WorkoutSessionResponse
from app.modules.workouts.service import WorkoutService

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.get("/sessions", response_model=list[WorkoutSessionResponse])
def list_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return WorkoutService(db).list_sessions(current_user)


@router.get("/today", response_model=WorkoutSessionResponse)
def today(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return WorkoutService(db).get_or_create_today(current_user)


@router.post("/sessions", response_model=WorkoutSessionResponse)
def create_session(payload: WorkoutSessionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return WorkoutService(db).create_session(current_user, payload)


@router.post("/sessions/{session_id}/complete", response_model=WorkoutSessionResponse)
def complete_session(session_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return WorkoutService(db).complete_session(current_user, session_id)


@router.post("/sessions/{session_id}/miss", response_model=WorkoutSessionResponse)
def miss_session(session_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return WorkoutService(db).miss_session(current_user, session_id)


@router.post("/sessions/{session_id}/reschedule", response_model=WorkoutSessionResponse)
def reschedule_session(
    session_id: UUID,
    payload: WorkoutRescheduleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return WorkoutService(db).reschedule_session(current_user, session_id, payload)
