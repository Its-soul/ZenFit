from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.agents.memory_agent import MemoryAgent
from app.ai.analytics.behavior_patterns import BehavioralPatternAnalyzer
from app.ai.analytics.personalization import PersonalizationEngine
from app.ai.analytics.predictors import PredictiveAnalyticsEngine
from app.ai.analytics.trend_detector import TrendDetector
from app.ai.observability import observe_ai_operation
from app.ai.reporting import WeeklyReportService
from app.modules.analytics.schemas import AnalyticsHistoryResponse, PredictiveAnalyticsResponse, WeeklyReportResponse
from app.modules.auth.models import User
from app.modules.nutrition.models import Meal
from app.modules.recovery.models import RecoveryCheckin
from app.modules.sleep.models import SleepLog
from app.modules.workouts.models import WorkoutSession


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.memory_agent = MemoryAgent()

    def predictive_summary(self, user: User) -> PredictiveAnalyticsResponse:
        with observe_ai_operation(
            self.db,
            operation="predictive_analytics.summary",
            user_id=user.id,
            agent_name="PredictiveAnalyticsEngine",
            input_summary="Behavioral pattern analysis with semantic memory retrieval",
        ) as audit:
            memories = self.memory_agent.retrieve(
                user_id=str(user.id),
                query="workout consistency missed sleep fatigue nutrition adherence motivation",
                limit=12,
            )
            patterns = BehavioralPatternAnalyzer(self.db).analyze(user.id)
            predictions = PredictiveAnalyticsEngine().predict(patterns=patterns, memories=memories)
            trends = TrendDetector().detect(patterns=patterns, predictions=predictions)
            personalization = PersonalizationEngine().build_profile(patterns=patterns, memories=memories)

            audit["retrieved_memory_ids"] = [memory["id"] for memory in memories]
            audit["scores"] = {key: value["score"] for key, value in predictions.items()}
            audit["output_summary"] = f"Generated {len(predictions)} predictions and {len(trends)} trends"

            return PredictiveAnalyticsResponse(
                patterns=patterns,
                predictions=predictions,
                trends=trends,
                personalization=personalization,
            )

    def latest_weekly_report(self, user: User) -> WeeklyReportResponse:
        report = WeeklyReportService(self.db).generate_for_user(user)
        self.db.commit()
        self.db.refresh(report)
        return WeeklyReportResponse(
            summary=report.summary,
            metrics=report.metrics,
            predictions=report.predictions,
            week_start=report.week_start.isoformat(),
            week_end=report.week_end.isoformat(),
        )

    def history(self, user: User, days: int = 90) -> AnalyticsHistoryResponse:
        days = max(7, min(days, 365))
        start_day = date.today() - timedelta(days=days - 1)
        start_datetime = datetime.combine(start_day, time.min, timezone.utc)

        workouts = list(self.db.scalars(select(WorkoutSession).where(WorkoutSession.user_id == user.id, WorkoutSession.scheduled_date >= start_day)))
        meals = list(self.db.scalars(select(Meal).where(Meal.user_id == user.id, Meal.logged_at >= start_datetime)))
        sleep_logs = list(self.db.scalars(select(SleepLog).where(SleepLog.user_id == user.id, SleepLog.sleep_date >= start_day)))
        recovery_logs = list(
            self.db.scalars(select(RecoveryCheckin).where(RecoveryCheckin.user_id == user.id, RecoveryCheckin.checkin_date >= start_day))
        )

        workouts_by_day = {}
        for workout in workouts:
            day = workout.scheduled_date
            workouts_by_day.setdefault(day, {"completed": 0, "missed": 0})
            if workout.status == "completed":
                workouts_by_day[day]["completed"] += 1
            if workout.status == "missed":
                workouts_by_day[day]["missed"] += 1

        meals_by_day = {}
        for meal in meals:
            day = meal.logged_at.date()
            meals_by_day.setdefault(day, {"calories": 0, "protein_g": 0.0})
            meals_by_day[day]["calories"] += meal.calories
            meals_by_day[day]["protein_g"] += meal.protein_g

        sleep_by_day = {item.sleep_date: item for item in sleep_logs}
        recovery_by_day = {item.checkin_date: item for item in recovery_logs}

        points = []
        for offset in range(days):
            current_day = start_day + timedelta(days=offset)
            workout_stats = workouts_by_day.get(current_day, {"completed": 0, "missed": 0})
            meal_stats = meals_by_day.get(current_day, {"calories": 0, "protein_g": 0.0})
            sleep = sleep_by_day.get(current_day)
            recovery = recovery_by_day.get(current_day)
            points.append(
                {
                    "date": current_day.isoformat(),
                    "workouts_completed": workout_stats["completed"],
                    "workouts_missed": workout_stats["missed"],
                    "calories": meal_stats["calories"],
                    "protein_g": round(meal_stats["protein_g"], 1),
                    "sleep_hours": sleep.duration_hours if sleep else None,
                    "readiness_score": recovery.readiness_score if recovery else None,
                }
            )

        return AnalyticsHistoryResponse(days=days, points=points)
