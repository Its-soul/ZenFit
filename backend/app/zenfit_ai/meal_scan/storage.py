import json
from app.core.redis_client import get_redis_client

TTL_SECONDS = 3600

class MealAnalysisStore:
    def save(self, *, user_id: str, analysis: dict) -> None:
        get_redis_client().setex(f"zenfit:meal-analysis:{analysis['analysis_id']}", TTL_SECONDS, json.dumps({"user_id": user_id, "analysis": analysis}))
    def get_for_user(self, *, user_id: str, analysis_id: str) -> dict | None:
        raw = get_redis_client().get(f"zenfit:meal-analysis:{analysis_id}")
        if not raw: return None
        value = json.loads(raw)
        return value["analysis"] if value.get("user_id") == user_id else None
    def delete(self, analysis_id: str) -> None:
        get_redis_client().delete(f"zenfit:meal-analysis:{analysis_id}")
