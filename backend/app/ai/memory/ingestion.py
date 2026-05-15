from app.ai.memory.chunking import chunk_text
from app.ai.memory.memory_writer import MemoryWriter


class MemoryIngestionPipeline:
    def __init__(self):
        self.writer = MemoryWriter()

    def ingest_event(self, *, user_id: str, event_type: str, text: str, metadata: dict | None = None) -> list[str]:
        metadata = metadata or {}
        metadata.update({"source": "domain_event", "event_type": event_type})

        memory_ids = []
        for chunk in chunk_text(text):
            memory_ids.append(self.writer.write(user_id=user_id, text=chunk, metadata=metadata))
        return memory_ids

