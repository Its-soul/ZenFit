from collections import Counter
from datetime import datetime, timedelta, timezone
from statistics import mean

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.events.models import DomainEvent
from app.modules.nutrition.models import Meal
from app.modules.recovery.models import RecoveryCheckin
from app.modules.sleep.models import SleepLog
from app.modules.workouts.models import WorkoutSession


class BehavioralPatternAnalyzer:
    def __init__(self, db: Session):
        self.db = db

    def analyze(self, user_id) -> dict:
        since = datetime.now(timezone.utc) - timedelta(days=30)
        workouts = list(self.db.scalars(select(WorkoutSession).where(WorkoutSession.user_id == user_id).order_by(WorkoutSession.scheduled_date.desc())))
        meals = list(self.db.scalars(select(Meal).where(Meal.user_id == user_id, Meal.logged_at >= since)))
        sleep_logs = list(self.db.scalars(select(SleepLog).where(SleepLog.user_id == user_id).order_by(SleepLog.sleep_date.desc()).limit(30)))
        recovery_logs = list(
            self.db.scalars(select(RecoveryCheckin).where(RecoveryCheckin.user_id == user_id).order_by(RecoveryCheckin.checkin_date.desc()).limit(30))
        )
        events = list(self.db.scalars(select(DomainEvent).where(DomainEvent.user_id == user_id, DomainEvent.created_at >= since)))

        completed = [workout for workout in workouts if workout.status == "completed"]
        missed = [workout for workout in workouts if workout.status == "missed"]
        meal_hours = [meal.logged_at.hour for meal in meals if meal.logged_at]
        event_counts = Counter(event.event_type for event in events)

        return {
            "workout_completion_rate": self._rate(len(completed), len(completed) + len(missed)),
            "missed_workout_count": len(missed),
            "preferred_workout_days": self._top_items([workout.scheduled_date.strftime("%A") for workout in completed]),
            "meal_timing_consistency": self._timing_consistency(meal_hours),
            "common_meal_hours": self._top_items(meal_hours),
            "average_sleep_hours": round(mean([log.duration_hours for log in sleep_logs]), 2) if sleep_logs else None,
            "average_sleep_quality": round(mean([log.quality_score for log in sleep_logs]), 1) if sleep_logs else None,
            "average_readiness": round(mean([log.readiness_score for log in recovery_logs]), 1) if recovery_logs else None,
            "fatigue_trend": self._trend([log.fatigue_score for log in reversed(recovery_logs)]),
            "readiness_trend": self._trend([log.readiness_score for log in reversed(recovery_logs)]),
            "event_counts": dict(event_counts),
            "motivation_triggers": self._motivation_triggers(events),
        }

    def _rate(self, numerator: int, denominator: int) -> float:
        if denominator == 0:
            return 0.0
        return round(numerator / denominator, 3)

    def _top_items(self, items: list, limit: int = 3) -> list:
        return [{"value": value, "count": count} for value, count in Counter(items).most_common(limit)]

    def _timing_consistency(self, hours: list[int]) -> float:
        if len(hours) < 2:
            return 0.0
        most_common_count = Counter(hours).most_common(1)[0][1]
        return round(most_common_count / len(hours), 3)

    def _trend(self, values: list[int]) -> str:
        if len(values) < 3:
            return "insufficient_data"
        first_half = values[: len(values) // 2]
        second_half = values[len(values) // 2 :]
        delta = mean(second_half) - mean(first_half)
        if delta > 1:
            return "rising"
        if delta < -1:
            return "falling"
        return "stable"

    def _motivation_triggers(self, events: list[DomainEvent]) -> list[str]:
        triggers = []
        if any(event.event_type == "workout.completed" for event in events):
            triggers.append("completion_feedback")
        if any(event.event_type == "plan.replanned" for event in events):
            triggers.append("adaptive_plan_changes")
        if any(event.event_type == "recommendation.generated" for event in events):
            triggers.append("small_next_action_prompts")
        return triggers

