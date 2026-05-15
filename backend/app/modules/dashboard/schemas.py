from pydantic import BaseModel

from app.modules.nutrition.schemas import NutritionTodayResponse
from app.modules.recommendations.schemas import RecommendationResponse
from app.modules.recovery.schemas import RecoveryCheckinResponse
from app.modules.sleep.schemas import SleepLogResponse
from app.modules.workouts.schemas import WorkoutSessionResponse


class DashboardTodayResponse(BaseModel):
    readiness_score: int | None
    adherence_score: int
    today_workout: WorkoutSessionResponse
    nutrition: NutritionTodayResponse
    latest_sleep: SleepLogResponse | None
    latest_recovery: RecoveryCheckinResponse | None
    recommendations: list[RecommendationResponse]

