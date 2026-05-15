from app.ai.agents.base_agent import AgentInput
from app.ai.agents.coach_agent import CoachAgent
from app.ai.agents.memory_agent import MemoryAgent
from app.ai.memory.context_builder import ContextBuilder


class CoachingOrchestrator:
    def __init__(self):
        self.memory_agent = MemoryAgent()
        self.context_builder = ContextBuilder()
        self.coach_agent = CoachAgent()

    def run(self, *, user_id: str, message: str, dashboard: dict) -> dict:
        memories = self.memory_agent.retrieve(user_id=user_id, query=message, limit=5)
        context = self.context_builder.build(dashboard=dashboard, memories=memories)
        output = self.coach_agent.run(AgentInput(user_id=user_id, message=message, context=context, memories=memories))

        if output.memory_to_write:
            self.memory_agent.write(
                user_id=user_id,
                text=output.memory_to_write,
                metadata={"source": "coach_conversation", "confidence": output.confidence},
            )

        return {
            "message": output.message,
            "recommendations": output.recommendations,
            "memories_used": memories,
            "confidence": output.confidence,
        }

