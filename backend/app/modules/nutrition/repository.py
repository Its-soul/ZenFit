from datetime import datetime, time
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.nutrition.models import Meal


class NutritionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_meal(self, user_id: UUID, payload) -> Meal:
        meal = Meal(user_id=user_id, **payload.model_dump(exclude_none=True))
        self.db.add(meal)
        self.db.flush()
        return meal

    def list_today(self, user_id: UUID) -> list[Meal]:
        start = datetime.combine(datetime.now().date(), time.min)
        end = datetime.combine(datetime.now().date(), time.max)
        return list(
            self.db.scalars(
                select(Meal)
                .where(Meal.user_id == user_id, Meal.logged_at >= start, Meal.logged_at <= end)
                .order_by(Meal.logged_at.desc())
            )
        )
