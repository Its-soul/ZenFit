from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.events.event_types import WORKOUT_COMPLETED, WORKOUT_MISSED, WORKOUT_RESCHEDULED
from app.events.producer import EventProducer
from app.modules.auth.models import User
from app.modules.workouts.repository import WorkoutRepository
from app.modules.workouts.schemas import WorkoutRescheduleRequest, WorkoutSessionCreate
from app.ai.predictions.adherence import predict_adherence
from app.ai.predictions.audit import PredictionAuditService


class WorkoutService:
    def __init__(self, db: Session):
        self.db = db
        self.workouts = WorkoutRepository(db)
        self.events = EventProducer(db)

    def list_sessions(self, user: User):
        return self.workouts.list_for_user(user.id)

    def get_or_create_today(self, user: User):
        today = date.today()
        session = self.workouts.get_for_date(user.id, today)
        if session:
            return session

        profile = user.profile
        title = "Full Body Foundation" if not profile or profile.fitness_level == "Beginner" else "Strength Progression"
        session = self.workouts.create(
            user.id,
            WorkoutSessionCreate(
                title=title,
                scheduled_date=today,
                planned_intensity="moderate",
                duration_minutes=45,
                notes="Auto-created from your onboarding preferences.",
            ),
        )
        self.db.flush(); self._record_shadow_prediction(user,session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def create_session(self, user: User, payload: WorkoutSessionCreate):
        self._validate_scheduled_date(payload.scheduled_date)
        session = self.workouts.create(user.id, payload)
        self.db.flush(); self._record_shadow_prediction(user,session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def complete_session(self, user: User, session_id: UUID):
        session = self._get_owned_session(user, session_id)
        self._ensure_transition_allowed(session.status, "completed")
        self._ensure_not_future_session(session)
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)
        PredictionAuditService(self.db).record_outcome(user_id=user.id,entity_id=session.id,outcome="completed")
        self.events.emit(
            user_id=user.id,
            event_type=WORKOUT_COMPLETED,
            payload={"session_id": str(session.id), "title": session.title, "planned_intensity": session.planned_intensity},
        )
        self.db.commit()
        self.db.refresh(session)
        return session

    def miss_session(self, user: User, session_id: UUID):
        session = self._get_owned_session(user, session_id)
        self._ensure_transition_allowed(session.status, "missed")
        self._ensure_not_future_session(session)
        session.status = "missed"
        session.completed_at = None
        PredictionAuditService(self.db).record_outcome(user_id=user.id,entity_id=session.id,outcome="missed")
        self.events.emit(
            user_id=user.id,
            event_type=WORKOUT_MISSED,
            payload={"session_id": str(session.id), "title": session.title, "planned_intensity": session.planned_intensity},
        )
        self.db.commit()
        self.db.refresh(session)
        return session

    def reschedule_session(self, user: User, session_id: UUID, payload: WorkoutRescheduleRequest):
        session = self._get_owned_session(user, session_id)
        self._ensure_transition_allowed(session.status, "rescheduled")
        self._validate_scheduled_date(payload.scheduled_date)
        if payload.scheduled_date == session.scheduled_date:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Choose a different date to reschedule this workout")

        replacement = self.workouts.get_for_date(user.id, payload.scheduled_date)
        if replacement is None:
            replacement = self.workouts.create(
                user.id,
                WorkoutSessionCreate(
                    title=session.title,
                    scheduled_date=payload.scheduled_date,
                    planned_intensity=session.planned_intensity,
                    duration_minutes=session.duration_minutes,
                    notes=f"Rescheduled from {session.scheduled_date.isoformat()}. {payload.reason or ''}".strip(),
                ),
            )
            self.db.flush(); self._record_shadow_prediction(user,replacement)
        else:
            replacement.notes = f"{replacement.notes or ''}\nReschedule note: {payload.reason or 'Moved from another session.'}".strip()

        session.status = "rescheduled"
        session.completed_at = None
        self.events.emit(
            user_id=user.id,
            event_type=WORKOUT_RESCHEDULED,
            payload={
                "source_session_id": str(session.id),
                "new_session_id": str(replacement.id),
                "from_date": session.scheduled_date.isoformat(),
                "to_date": payload.scheduled_date.isoformat(),
                "reason": payload.reason,
            },
        )
        self.db.commit()
        self.db.refresh(replacement)
        return replacement

    def _get_owned_session(self, user: User, session_id: UUID):
        session = self.workouts.get_by_id_for_user(session_id, user.id)
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout session not found")
        return session

    def _ensure_transition_allowed(self, current_status: str, next_status: str) -> None:
        if current_status != "scheduled":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot mark a {current_status} workout as {next_status}. Completed, missed, and rescheduled workouts are final states.",
            )

    def _ensure_not_future_session(self, session) -> None:
        if session.scheduled_date > date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Future workouts cannot be completed or missed yet")

    def _validate_scheduled_date(self, scheduled_date: date) -> None:
        if scheduled_date > date.today() + timedelta(days=366):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Workout dates must be within the next year")

    def _record_shadow_prediction(self,user:User,session)->None:
        features={"scheduled_hour":18,"day_of_week":session.scheduled_date.weekday(),"weekend_flag":int(session.scheduled_date.weekday()>=5)}
        prediction=predict_adherence(features)
        PredictionAuditService(self.db).record(user_id=user.id,prediction_type="adherence",entity_id=session.id,value=prediction.miss_probability,risk_level=prediction.risk_level,features=features,model_name=prediction.source,shadow_mode=prediction.shadow_mode)
