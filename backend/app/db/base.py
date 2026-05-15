from app.db.base_class import Base


# Import models so Alembic can discover them from Base.metadata.
from app.modules.auth.models import User  # noqa: E402,F401
from app.modules.users.models import UserProfile  # noqa: E402,F401
from app.modules.workouts.models import WorkoutSession  # noqa: E402,F401
from app.modules.nutrition.models import Meal  # noqa: E402,F401
from app.modules.sleep.models import SleepLog  # noqa: E402,F401
from app.modules.recovery.models import RecoveryCheckin  # noqa: E402,F401
from app.modules.recommendations.models import Recommendation  # noqa: E402,F401
from app.modules.recommendations.feedback_models import RecommendationFeedback  # noqa: E402,F401
from app.events.models import DomainEvent  # noqa: E402,F401
from app.ai.observability import AIAuditLog  # noqa: E402,F401
from app.ai.reports import AIWeeklyReport  # noqa: E402,F401
