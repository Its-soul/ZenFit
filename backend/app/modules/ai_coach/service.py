import json

from sqlalchemy.orm import Session

from app.ai.orchestrators.coaching_orchestrator import CoachingOrchestrator
from app.ai.observability import observe_ai_operation
from app.ai.tools.user_context_tools import UserContextTools
from app.modules.auth.models import User
from app.modules.ai_coach.schemas import CoachMessageRequest


class AICoachService:
    def __init__(self, db: Session):
        self.db = db
        self.orchestrator = CoachingOrchestrator()
        self.tools = UserContextTools(db)

    def send_message(self, user: User, payload: CoachMessageRequest) -> dict:
        with observe_ai_operation(
            self.db,
            operation="ai_coach.message",
            user_id=user.id,
            agent_name="CoachAgent",
            prompt_name="coach.md",
            input_summary=payload.message[:300],
        ) as audit:
            dashboard = self.tools.get_dashboard_context(user)
            response = self.orchestrator.run(user_id=str(user.id), message=payload.message, dashboard=dashboard)
            audit["output_summary"] = response["message"][:500]
            audit["retrieved_memory_ids"] = [memory["id"] for memory in response.get("memories_used", [])]
            audit["tool_calls"] = [{"tool": "get_dashboard_context"}]
            audit["scores"] = {"confidence": response.get("confidence", 0)}
            self.db.commit()
            return response

    def stream_message(self, user: User, payload: CoachMessageRequest):
        response = self.send_message(user, payload)
        words = response["message"].split(" ")
        for word in words:
            yield f"data: {word} \n\n"
        yield f"event: metadata\ndata: {json.dumps(response, default=str)}\n\n"
        yield "event: done\ndata: ok\n\n"
