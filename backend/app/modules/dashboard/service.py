from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.dashboard.schemas import DashboardTodayResponse
from app.modules.nutrition.service import NutritionService
from app.modules.recommendations.service import RecommendationService
from app.modules.recovery.service import RecoveryService
from app.modules.sleep.service import SleepService
from app.modules.workouts.service import WorkoutService


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def today(self, user: User) -> DashboardTodayResponse:
        workout = WorkoutService(self.db).get_or_create_today(user)
        nutrition = NutritionService(self.db).today(user)
        sleep_logs = SleepService(self.db).list_recent(user)
        recovery = RecoveryService(self.db).latest(user)
        recommendations = RecommendationService(self.db).list_active(user)

        readiness = recovery.readiness_score if recovery else 82
        adherence = self._basic_adherence_score(workout.status, nutrition.calories, sleep_logs)

        return DashboardTodayResponse(
            readiness_score=readiness,
            adherence_score=adherence,
            today_workout=workout,
            nutrition=nutrition,
            latest_sleep=sleep_logs[0] if sleep_logs else None,
            latest_recovery=recovery,
            recommendations=recommendations,
        )

    @staticmethod
    def _basic_adherence_score(workout_status: str, calories: int, sleep_logs: list) -> int:
        score = 60
        if workout_status == "completed":
            score += 20
        if calories > 0:
            score += 10
        if sleep_logs:
            score += 10
        return min(score, 100)

