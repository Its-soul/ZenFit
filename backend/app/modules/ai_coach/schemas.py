from pydantic import BaseModel, Field


class CoachMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class CoachMessageResponse(BaseModel):
    message: str
    recommendations: list[dict]
    memories_used: list[dict]
    confidence: float

