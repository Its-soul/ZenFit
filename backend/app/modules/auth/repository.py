from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: UUID) -> User | None:
        return self.db.scalar(select(User).where(User.id == user_id))

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email.lower()))

    def list_active(self, limit: int = 500) -> list[User]:
        return list(self.db.scalars(select(User).where(User.is_active.is_(True)).limit(limit)))

    def create(self, *, email: str, full_name: str, hashed_password: str) -> User:
        user = User(email=email.lower(), full_name=full_name, hashed_password=hashed_password)
        self.db.add(user)
        self.db.flush()
        return user
