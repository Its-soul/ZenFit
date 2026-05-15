from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.recovery.models import RecoveryCheckin


class RecoveryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: UUID, payload, readiness_score: int) -> RecoveryCheckin:
        existing = self.db.scalar(
            select(RecoveryCheckin).where(RecoveryCheckin.user_id == user_id, RecoveryCheckin.checkin_date == payload.checkin_date)
        )
        if existing:
            existing.fatigue_score = payload.fatigue_score
            existing.soreness_score = payload.soreness_score
            existing.stress_score = payload.stress_score
            existing.readiness_score = readiness_score
            existing.notes = payload.notes
            self.db.flush()
            return existing

        checkin = RecoveryCheckin(user_id=user_id, readiness_score=readiness_score, **payload.model_dump())
        self.db.add(checkin)
        self.db.flush()
        return checkin

    def latest(self, user_id: UUID) -> RecoveryCheckin | None:
        return self.db.scalar(
            select(RecoveryCheckin).where(RecoveryCheckin.user_id == user_id).order_by(RecoveryCheckin.checkin_date.desc()).limit(1)
        )

