from app.ai.memory.reranker import MemoryReranker


def run_retrieval_quality_tests() -> list[dict]:
    memories = [
        {"id": "1", "score": 0.76, "text": "User missed a workout after poor sleep.", "metadata": {"importance": 0.9, "category": "adherence"}},
        {"id": "2", "score": 0.82, "text": "User logged lunch.", "metadata": {"importance": 0.3, "category": "nutrition"}},
    ]
    ranked = MemoryReranker().rerank(memories)
    return [
        {
            "name": "important_adherence_memory_ranks_first",
            "passed": ranked[0]["id"] == "1",
            "top_memory_id": ranked[0]["id"],
        }
    ]

