from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.sleep.models import SleepLog


class SleepRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: UUID, payload) -> SleepLog:
        existing = self.db.scalar(select(SleepLog).where(SleepLog.user_id == user_id, SleepLog.sleep_date == payload.sleep_date))
        if existing:
            existing.duration_hours = payload.duration_hours
            existing.quality_score = payload.quality_score
            existing.notes = payload.notes
            self.db.flush()
            return existing

        sleep = SleepLog(user_id=user_id, **payload.model_dump())
        self.db.add(sleep)
        self.db.flush()
        return sleep

    def list_recent(self, user_id: UUID, limit: int = 14) -> list[SleepLog]:
        return list(
            self.db.scalars(select(SleepLog).where(SleepLog.user_id == user_id).order_by(SleepLog.sleep_date.desc()).limit(limit))
        )

