class ContextBuilder:
    def build(self, *, dashboard: dict, memories: list[dict]) -> dict:
        workout_memories = [memory for memory in memories if memory.get("metadata", {}).get("category") == "workout"]
        nutrition_memories = [memory for memory in memories if memory.get("metadata", {}).get("category") == "nutrition"]
        sleep_memories = [memory for memory in memories if memory.get("metadata", {}).get("category") == "sleep"]
        adherence_memories = [memory for memory in memories if memory.get("metadata", {}).get("category") == "adherence"]

        return {
            "dashboard": dashboard,
            "memory_summary": [memory["text"] for memory in memories],
            "behavior_memory": {
                "workout_consistency": [memory["text"] for memory in workout_memories[:3]],
                "nutrition_habits": [memory["text"] for memory in nutrition_memories[:3]],
                "sleep_trends": [memory["text"] for memory in sleep_memories[:3]],
                "adherence_patterns": [memory["text"] for memory in adherence_memories[:3]],
            },
        }
