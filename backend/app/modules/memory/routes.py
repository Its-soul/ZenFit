from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.memory.schemas import MemorySearchRequest, MemorySearchResponse
from app.modules.memory.service import MemoryService

router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("/search", response_model=MemorySearchResponse)
def search_memory(payload: MemorySearchRequest, current_user: User = Depends(get_current_user)):
    return MemoryService().search(current_user, payload)

