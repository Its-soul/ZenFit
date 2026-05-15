from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.analytics.behavior_patterns import BehavioralPatternAnalyzer
from app.ai.analytics.predictors import PredictiveAnalyticsEngine
from app.ai.reports import AIWeeklyReport
from app.modules.auth.models import User


class WeeklyReportService:
    def __init__(self, db: Session):
        self.db = db

    def generate_for_user(self, user: User, today: date | None = None) -> AIWeeklyReport:
        today = today or date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        existing = self.db.scalar(
            select(AIWeeklyReport).where(AIWeeklyReport.user_id == user.id, AIWeeklyReport.week_start == week_start)
        )
        patterns = BehavioralPatternAnalyzer(self.db).analyze(user.id)
        predictions = PredictiveAnalyticsEngine().predict(patterns=patterns, memories=[])
        summary = self._summary(patterns=patterns, predictions=predictions)

        if existing:
            existing.summary = summary
            existing.metrics = patterns
            existing.predictions = predictions
            self.db.flush()
            return existing

        report = AIWeeklyReport(
            user_id=user.id,
            week_start=week_start,
            week_end=week_end,
            summary=summary,
            metrics=patterns,
            predictions=predictions,
        )
        self.db.add(report)
        self.db.flush()
        return report

    def _summary(self, *, patterns: dict, predictions: dict) -> str:
        completion_rate = round(patterns.get("workout_completion_rate", 0) * 100)
        adherence = predictions.get("adherence_risk", {}).get("level", "unknown")
        recovery = predictions.get("recovery_decline", {}).get("level", "unknown")
        return (
            f"Weekly AI review: workout completion is {completion_rate}%. "
            f"Adherence risk is {adherence}, and recovery decline risk is {recovery}. "
            "Use the next recommendations to protect consistency."
        )

