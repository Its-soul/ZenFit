from app.ai.memory.memory_writer import MemoryWriter
from app.ai.memory.retriever import MemoryRetriever


class MemoryAgent:
    def __init__(self):
        self.retriever = MemoryRetriever()
        self.writer = MemoryWriter()

    def retrieve(self, *, user_id: str, query: str, limit: int = 5) -> list[dict]:
        return self.retriever.retrieve(user_id=user_id, query=query, limit=limit)

    def write(self, *, user_id: str, text: str, metadata: dict | None = None) -> None:
        self.writer.write(user_id=user_id, text=text, metadata=metadata or {})

