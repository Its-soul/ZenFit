import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base

class AIPrediction(Base):
    __tablename__="ai_predictions"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"),index=True)
    prediction_type: Mapped[str]=mapped_column(String(40),index=True)
    entity_id: Mapped[uuid.UUID|None]=mapped_column(UUID(as_uuid=True),nullable=True,index=True)
    model_name: Mapped[str]=mapped_column(String(120))
    model_version: Mapped[str]=mapped_column(String(80))
    prediction_value: Mapped[float]=mapped_column(Float)
    risk_level: Mapped[str|None]=mapped_column(String(30),nullable=True)
    feature_snapshot: Mapped[dict]=mapped_column(JSONB,default=dict)
    shadow_mode: Mapped[bool]=mapped_column(Boolean,default=True)
    outcome: Mapped[str|None]=mapped_column(String(30),nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),index=True)
    outcome_recorded_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
