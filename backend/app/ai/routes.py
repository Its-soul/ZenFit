from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.config import settings
from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.ai.pose.analyzer import PoseAnalyzer
from app.ai.schemas import PoseRequest
from app.ai.service import ZenFitAIService
from app.ai.memory.semantic_retriever import MemoryRetriever

router = APIRouter(prefix="/ai", tags=["zenfit-ai"]); analyzer = PoseAnalyzer()

class MemoryDebugRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)

@router.get("/health")
def health(_: User = Depends(get_current_user)): return ZenFitAIService().health()

@router.post("/pose/analyze")
def analyze_pose(payload: PoseRequest, _: User = Depends(get_current_user)):
    try: return analyzer.analyze(payload.exercise, payload.landmarks, payload.timestamp)
    except ValueError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.post("/memory/debug-search")
def debug_memory(payload: MemoryDebugRequest, current_user: User = Depends(get_current_user)):
    if settings.app_env.lower() not in {"development", "test"}:
        raise HTTPException(status_code=404, detail="Not found")
    results = MemoryRetriever().search(user_id=str(current_user.id), query=payload.query, debug=True)
    return {"query": payload.query, "candidate_count": len(results), "results": [{"text": item["text"], "vector_score": item.get("score"), "rerank_score": item.get("rerank_score"), "category": item.get("metadata",{}).get("category")} for item in results]}
