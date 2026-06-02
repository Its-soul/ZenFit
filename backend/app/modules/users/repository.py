from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.users.models import UserProfile


class UserProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: UUID) -> UserProfile | None:
        return self.db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))

    def create_for_user(self, user_id: UUID) -> UserProfile:
        profile = UserProfile(user_id=user_id)
        self.db.add(profile)
        self.db.flush()
        return profile

    def save_onboarding(
        self,
        *,
        user_id: UUID,
        primary_goal: str,
        fitness_level: str,
        preferred_training_days: int,
        preferred_unit: str,
        weight_kg: float | None,
        height_cm: float | None,
        age: int | None,
        biological_sex: str | None,
    ) -> UserProfile:
        profile = self.get_by_user_id(user_id)
        if profile is None:
            profile = self.create_for_user(user_id)

        profile.primary_goal = primary_goal
        profile.fitness_level = fitness_level
        profile.preferred_training_days = preferred_training_days
        profile.preferred_unit = preferred_unit
        profile.weight_kg = weight_kg
        profile.height_cm = height_cm
        profile.age = age
        profile.biological_sex = biological_sex
        profile.onboarding_complete = True
        self.db.flush()
        return profile
