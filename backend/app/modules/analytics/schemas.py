from pydantic import BaseModel


class PredictiveAnalyticsResponse(BaseModel):
    patterns: dict
    predictions: dict
    trends: list[dict]
    personalization: dict


class WeeklyReportResponse(BaseModel):
    summary: str
    metrics: dict
    predictions: dict
    week_start: str
    week_end: str


class AnalyticsHistoryPoint(BaseModel):
    date: str
    workouts_completed: int
    workouts_missed: int
    calories: int
    protein_g: float
    calorie_target: int
    protein_target_g: float
    sleep_hours: float | None
    readiness_score: int | None


class AnalyticsHistoryResponse(BaseModel):
    days: int
    points: list[AnalyticsHistoryPoint]
