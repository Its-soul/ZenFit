from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RecommendationResponse(BaseModel):
    id: UUID
    title: str
    body: str
    category: str
    priority: str
    status: str
    source_event_type: str | None
    confidence_score: float
    reasoning_summary: str | None
    triggering_factors: list
    related_memory_ids: list
    created_at: datetime

    model_config = {"from_attributes": True}


class RecommendationFeedbackRequest(BaseModel):
    feedback_type: str
    notes: str | None = None
