import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class RecoveryCheckin(Base):
    __tablename__ = "recovery_checkins"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    checkin_date: Mapped[date] = mapped_column(Date, nullable=False)
    fatigue_score: Mapped[int] = mapped_column(Integer, nullable=False)
    soreness_score: Mapped[int] = mapped_column(Integer, nullable=False)
    stress_score: Mapped[int] = mapped_column(Integer, nullable=False)
    readiness_score: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

