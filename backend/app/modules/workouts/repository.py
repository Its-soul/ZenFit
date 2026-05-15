from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.workouts.models import WorkoutSession


class WorkoutRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id_for_user(self, session_id: UUID, user_id: UUID) -> WorkoutSession | None:
        return self.db.scalar(select(WorkoutSession).where(WorkoutSession.id == session_id, WorkoutSession.user_id == user_id))

    def list_for_user(self, user_id: UUID, limit: int = 30) -> list[WorkoutSession]:
        return list(
            self.db.scalars(
                select(WorkoutSession)
                .where(WorkoutSession.user_id == user_id)
                .order_by(WorkoutSession.scheduled_date.desc())
                .limit(limit)
            )
        )

    def get_for_date(self, user_id: UUID, scheduled_date: date) -> WorkoutSession | None:
        return self.db.scalar(
            select(WorkoutSession).where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.scheduled_date == scheduled_date,
            )
        )

    def create(self, user_id: UUID, payload) -> WorkoutSession:
        session = WorkoutSession(user_id=user_id, **payload.model_dump())
        self.db.add(session)
        self.db.flush()
        return session

