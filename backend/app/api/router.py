from fastapi import APIRouter

from app.ai.routes import router as ai_router
from app.modules.ai_coach.routes import router as ai_coach_router
from app.modules.analytics.routes import router as analytics_router
from app.modules.auth.routes import router as auth_router
from app.modules.dashboard.routes import router as dashboard_router
from app.modules.memory.routes import router as memory_router
from app.modules.nutrition.routes import router as nutrition_router
from app.modules.recommendations.routes import router as recommendations_router
from app.modules.recovery.routes import router as recovery_router
from app.modules.sleep.routes import router as sleep_router
from app.modules.users.routes import router as users_router
from app.modules.workouts.routes import router as workouts_router

api_router = APIRouter()
for router in (
    auth_router,
    users_router,
    ai_coach_router,
    memory_router,
    dashboard_router,
    workouts_router,
    nutrition_router,
    sleep_router,
    recovery_router,
    recommendations_router,
    analytics_router,
    ai_router,
):
    api_router.include_router(router)
