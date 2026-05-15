from app.ai.memory.retriever import MemoryRetriever
from app.modules.auth.models import User
from app.modules.memory.schemas import MemorySearchRequest, MemorySearchResponse


class MemoryService:
    def __init__(self):
        self.retriever = MemoryRetriever()

    def search(self, user: User, payload: MemorySearchRequest) -> MemorySearchResponse:
        memories = self.retriever.retrieve(user_id=str(user.id), query=payload.query, limit=payload.limit)
        return MemorySearchResponse(results=memories)

