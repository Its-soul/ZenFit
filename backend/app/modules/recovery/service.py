from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.events.event_types import RECOVERY_LOW
from app.events.producer import EventProducer
from app.modules.auth.models import User
from app.modules.recovery.repository import RecoveryRepository
from app.modules.recovery.schemas import RecoveryCheckinCreate


class RecoveryService:
    def __init__(self, db: Session):
        self.db = db
        self.recovery = RecoveryRepository(db)
        self.events = EventProducer(db)

    def latest(self, user: User):
        return self.recovery.latest(user.id)

    def create(self, user: User, payload: RecoveryCheckinCreate):
        if payload.checkin_date > date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Recovery check-ins cannot be created for future dates")
        readiness = self.calculate_readiness(payload.fatigue_score, payload.soreness_score, payload.stress_score)
        checkin = self.recovery.create(user.id, payload, readiness)
        if readiness < 55:
            self.events.emit(user_id=user.id, event_type=RECOVERY_LOW, payload={"checkin_id": str(checkin.id), "readiness": readiness})
        self.db.commit()
        self.db.refresh(checkin)
        return checkin

    @staticmethod
    def calculate_readiness(fatigue: int, soreness: int, stress: int) -> int:
        strain = (fatigue + soreness + stress) / 30
        return max(1, min(100, round(100 - strain * 70)))
