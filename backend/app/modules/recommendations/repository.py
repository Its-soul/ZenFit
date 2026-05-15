from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.recommendations.feedback_models import RecommendationFeedback
from app.modules.recommendations.models import Recommendation


class RecommendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_active(self, user_id: UUID) -> list[Recommendation]:
        self.expire_stale(user_id)
        items = list(
            self.db.scalars(
                select(Recommendation)
                .where(Recommendation.user_id == user_id, Recommendation.status == "active")
                .order_by(Recommendation.confidence_score.desc(), Recommendation.created_at.desc())
                .limit(20)
            )
        )
        return self._dedupe_in_memory(items)[:8]

    def expire_stale(self, user_id: UUID, days: int = 14) -> None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stale_items = list(
            self.db.scalars(
                select(Recommendation).where(
                    Recommendation.user_id == user_id,
                    Recommendation.status == "active",
                    Recommendation.created_at < cutoff,
                )
            )
        )
        for item in stale_items:
            item.status = "expired"

    def get_for_user(self, *, recommendation_id: UUID, user_id: UUID) -> Recommendation | None:
        return self.db.scalar(select(Recommendation).where(Recommendation.id == recommendation_id, Recommendation.user_id == user_id))

    def create(
        self,
        *,
        user_id: UUID,
        title: str,
        body: str,
        category: str,
        priority: str = "normal",
        source_event_type: str | None = None,
        confidence_score: float = 0.6,
        reasoning_summary: str | None = None,
        triggering_factors: list | None = None,
        related_memory_ids: list | None = None,
    ):
        existing = self.find_similar_active(
            user_id=user_id,
            title=title,
            category=category,
            source_event_type=source_event_type,
        )
        if existing:
            existing._was_merged = True
            existing.body = body
            existing.priority = self._higher_priority(existing.priority, priority)
            existing.confidence_score = max(existing.confidence_score, confidence_score)
            existing.reasoning_summary = reasoning_summary or existing.reasoning_summary
            existing.triggering_factors = sorted(set((existing.triggering_factors or []) + (triggering_factors or [])))
            existing.related_memory_ids = list(dict.fromkeys((existing.related_memory_ids or []) + (related_memory_ids or [])))[:12]
            self.db.flush()
            return existing

        item = Recommendation(
            user_id=user_id,
            title=title,
            body=body,
            category=category,
            priority=priority,
            source_event_type=source_event_type,
            confidence_score=confidence_score,
            reasoning_summary=reasoning_summary,
            triggering_factors=triggering_factors or [],
            related_memory_ids=related_memory_ids or [],
        )
        item._was_merged = False
        self.db.add(item)
        self.db.flush()
        return item

    def find_similar_active(
        self,
        *,
        user_id: UUID,
        title: str,
        category: str,
        source_event_type: str | None,
    ) -> Recommendation | None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        normalized_title = title.strip().lower()
        candidates = list(
            self.db.scalars(
                select(Recommendation).where(
                    Recommendation.user_id == user_id,
                    Recommendation.status == "active",
                    Recommendation.category == category,
                    Recommendation.created_at >= cutoff,
                )
            )
        )
        for candidate in candidates:
            if candidate.title.strip().lower() == normalized_title:
                return candidate
            if source_event_type and candidate.source_event_type == source_event_type and self._similar_words(candidate.title, title):
                return candidate
        return None

    def add_feedback(self, *, recommendation_id: UUID, user_id: UUID, feedback_type: str, notes: str | None = None) -> RecommendationFeedback:
        feedback = RecommendationFeedback(
            recommendation_id=recommendation_id,
            user_id=user_id,
            feedback_type=feedback_type,
            notes=notes,
        )
        self.db.add(feedback)
        recommendation = self.get_for_user(recommendation_id=recommendation_id, user_id=user_id)
        if recommendation and feedback_type in {"accepted", "dismissed"}:
            recommendation.status = feedback_type
        self.db.flush()
        return feedback

    def _dedupe_in_memory(self, items: list[Recommendation]) -> list[Recommendation]:
        seen = set()
        deduped = []
        for item in items:
            key = (item.category, item.title.strip().lower())
            if key in seen:
                continue
            seen.add(key)
            deduped.append(item)
        return deduped

    def _similar_words(self, first: str, second: str) -> bool:
        first_words = {word for word in first.lower().split() if len(word) > 3}
        second_words = {word for word in second.lower().split() if len(word) > 3}
        if not first_words or not second_words:
            return False
        return len(first_words & second_words) >= 2

    def _higher_priority(self, current: str, incoming: str) -> str:
        order = {"low": 0, "normal": 1, "high": 2}
        return incoming if order.get(incoming, 1) > order.get(current, 1) else current
