import uuid
from datetime import datetime
from sqlalchemy import Boolean,DateTime,ForeignKey,String,func
from sqlalchemy.dialects.postgresql import JSONB,UUID
from sqlalchemy.orm import Mapped,mapped_column
from app.db.base_class import Base

class MealAnalysisCorrection(Base):
    __tablename__="meal_analysis_corrections"
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"),index=True)
    analysis_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),index=True)
    predicted_foods:Mapped[list]=mapped_column(JSONB,default=list)
    confirmed_foods:Mapped[list]=mapped_column(JSONB,default=list)
    model_versions:Mapped[list]=mapped_column(JSONB,default=list)
    training_consent:Mapped[bool]=mapped_column(Boolean,default=False,nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
