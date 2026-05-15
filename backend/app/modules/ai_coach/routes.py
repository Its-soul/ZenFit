from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.modules.ai_coach.schemas import CoachMessageRequest, CoachMessageResponse
from app.modules.ai_coach.service import AICoachService
from app.modules.auth.models import User

router = APIRouter(prefix="/ai-coach", tags=["ai-coach"])


@router.post("/messages", response_model=CoachMessageResponse)
def send_message(payload: CoachMessageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AICoachService(db).send_message(current_user, payload)


@router.post("/messages/stream")
def stream_message(payload: CoachMessageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return StreamingResponse(AICoachService(db).stream_message(current_user, payload), media_type="text/event-stream")
