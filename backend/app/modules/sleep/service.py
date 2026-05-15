from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.events.event_types import SLEEP_LOGGED, SLEEP_POOR
from app.events.producer import EventProducer
from app.modules.auth.models import User
from app.modules.sleep.repository import SleepRepository
from app.modules.sleep.schemas import SleepLogCreate


class SleepService:
    def __init__(self, db: Session):
        self.db = db
        self.sleep = SleepRepository(db)
        self.events = EventProducer(db)

    def list_recent(self, user: User):
        return self.sleep.list_recent(user.id)

    def create(self, user: User, payload: SleepLogCreate):
        if payload.sleep_date > date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sleep logs cannot be created for future dates")
        sleep = self.sleep.create(user.id, payload)
        self.events.emit(
            user_id=user.id,
            event_type=SLEEP_LOGGED,
            payload={"sleep_log_id": str(sleep.id), "duration_hours": sleep.duration_hours, "quality_score": sleep.quality_score},
        )
        if sleep.duration_hours < 6 or sleep.quality_score < 55:
            self.events.emit(
                user_id=user.id,
                event_type=SLEEP_POOR,
                payload={"sleep_log_id": str(sleep.id), "duration_hours": sleep.duration_hours, "quality_score": sleep.quality_score},
            )
        self.db.commit()
        self.db.refresh(sleep)
        return sleep
