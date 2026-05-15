from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.dashboard.service import DashboardService


class UserContextTools:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_context(self, user: User) -> dict:
        return DashboardService(self.db).today(user).model_dump(mode="json")

