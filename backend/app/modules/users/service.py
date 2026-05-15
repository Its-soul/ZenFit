from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.users.repository import UserProfileRepository
from app.modules.users.schemas import OnboardingRequest, UserProfileResponse


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.profiles = UserProfileRepository(db)

    def get_profile(self, user: User) -> UserProfileResponse:
        profile = self.profiles.get_by_user_id(user.id) or self.profiles.create_for_user(user.id)
        self.db.commit()
        self.db.refresh(profile)
        return UserProfileResponse.model_validate(profile)

    def complete_onboarding(self, user: User, payload: OnboardingRequest) -> UserProfileResponse:
        profile = self.profiles.save_onboarding(
            user_id=user.id,
            primary_goal=payload.primary_goal,
            fitness_level=payload.fitness_level,
            preferred_training_days=payload.preferred_training_days,
            preferred_unit=payload.preferred_unit,
        )
        self.db.commit()
        self.db.refresh(profile)
        return UserProfileResponse.model_validate(profile)

