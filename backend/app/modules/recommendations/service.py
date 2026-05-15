from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status

from app.modules.auth.models import User
from app.modules.recommendations.repository import RecommendationRepository
from app.modules.recommendations.schemas import RecommendationFeedbackRequest


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.recommendations = RecommendationRepository(db)

    def list_active(self, user: User):
        items = self.recommendations.list_active(user.id)
        if items:
            self.db.commit()
            return items

        starter = self.recommendations.create(
            user_id=user.id,
            title="Log your first meal today",
            body="Nutrition data gives the adaptive system a stronger signal for coaching and plan adjustments.",
            category="nutrition",
            priority="normal",
            confidence_score=0.52,
            reasoning_summary="Starter recommendation shown because no active recommendation history exists.",
            triggering_factors=["new_user", "missing_nutrition_signal"],
        )
        self.db.commit()
        self.db.refresh(starter)
        return [starter]

    def add_feedback(self, user: User, recommendation_id: UUID, payload: RecommendationFeedbackRequest):
        recommendation = self.recommendations.get_for_user(recommendation_id=recommendation_id, user_id=user.id)
        if recommendation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")
        feedback = self.recommendations.add_feedback(
            recommendation_id=recommendation_id,
            user_id=user.id,
            feedback_type=payload.feedback_type,
            notes=payload.notes,
        )
        self.db.commit()
        self.db.refresh(feedback)
        return {"status": "saved", "feedback_type": feedback.feedback_type}
