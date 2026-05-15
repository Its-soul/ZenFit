from app.ai.memory.vector_store import VectorStore
from app.ai.memory.reranker import MemoryReranker


class MemoryRetriever:
    def __init__(self):
        self.vector_store = VectorStore()
        self.reranker = MemoryReranker()

    def retrieve(self, *, user_id: str, query: str, limit: int = 5) -> list[dict]:
        memories = self.vector_store.search_memory(user_id=user_id, query=query, limit=limit)
        return self.reranker.rerank(memories)
