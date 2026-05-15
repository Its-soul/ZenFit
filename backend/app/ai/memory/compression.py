from collections import defaultdict

from app.ai.memory.memory_writer import MemoryWriter


class MemoryCompressor:
    def __init__(self):
        self.writer = MemoryWriter()

    def summarize(self, *, user_id: str, memories: list[dict]) -> str | None:
        if len(memories) < 3:
            return None

        grouped = defaultdict(list)
        for memory in memories:
            category = memory.get("metadata", {}).get("category", "general")
            grouped[category].append(memory.get("text", ""))

        parts = []
        for category, texts in grouped.items():
            if texts:
                parts.append(f"{category}: {self._compact_texts(texts[:5])}")

        summary = "Long-term behavior summary. " + " ".join(parts)
        self.writer.write(
            user_id=user_id,
            text=summary,
            metadata={"category": "summary", "source": "memory_compression", "importance": 0.82},
        )
        return summary

    def _compact_texts(self, texts: list[str]) -> str:
        joined = " ".join(texts)
        words = joined.split()
        return " ".join(words[:70])

