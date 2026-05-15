from pydantic import BaseModel, Field


class MemorySearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=8, ge=1, le=20)


class MemorySearchResult(BaseModel):
    id: str
    score: float
    text: str
    metadata: dict


class MemorySearchResponse(BaseModel):
    results: list[MemorySearchResult]

