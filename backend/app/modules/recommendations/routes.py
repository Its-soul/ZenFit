from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.recommendations.schemas import RecommendationFeedbackRequest, RecommendationResponse
from app.modules.recommendations.service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=list[RecommendationResponse])
def list_active(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return RecommendationService(db).list_active(current_user)


@router.post("/{recommendation_id}/feedback")
def add_feedback(
    recommendation_id: UUID,
    payload: RecommendationFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return RecommendationService(db).add_feedback(current_user, recommendation_id, payload)
