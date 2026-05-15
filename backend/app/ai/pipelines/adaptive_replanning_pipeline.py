from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.agents.base_agent import AgentInput
from app.ai.agents.memory_agent import MemoryAgent
from app.ai.agents.recovery_agent import RecoveryAgent
from app.ai.agents.replanning_agent import ReplanningAgent
from app.ai.memory.context_builder import ContextBuilder
from app.events.event_types import PLAN_REPLANNED
from app.events.producer import EventProducer
from app.modules.auth.models import User
from app.modules.dashboard.service import DashboardService
from app.modules.workouts.repository import WorkoutRepository
from app.modules.workouts.schemas import WorkoutSessionCreate


class AdaptiveReplanningPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.memory_agent = MemoryAgent()
        self.context_builder = ContextBuilder()
        self.recovery_agent = RecoveryAgent()
        self.replanning_agent = ReplanningAgent()
        self.workouts = WorkoutRepository(db)
        self.events = EventProducer(db)

    def run_for_missed_workout(self, *, user: User, source_event_id: UUID) -> dict:
        dashboard = DashboardService(self.db).today(user).model_dump(mode="json")
        memories = self.memory_agent.retrieve(
            user_id=str(user.id),
            query="missed workout consistency adherence fatigue sleep recovery",
            limit=8,
        )
        context = self.context_builder.build(dashboard=dashboard, memories=memories)

        recovery_output = self.recovery_agent.run(
            AgentInput(user_id=str(user.id), message="evaluate recovery for missed workout", context=context, memories=memories)
        )
        context["dashboard"]["readiness_score"] = recovery_output.recommendations[0]["readiness_score"]

        replanning_output = self.replanning_agent.run(
            AgentInput(user_id=str(user.id), message="replan missed workout", context=context, memories=memories)
        )
        plan = replanning_output.recommendations[0]

        scheduled_date = date.fromisoformat(plan["scheduled_date"])
        existing = self.workouts.get_for_date(user.id, scheduled_date)
        if existing is None:
            new_session = self.workouts.create(
                user.id,
                WorkoutSessionCreate(
                    title=plan["title"],
                    scheduled_date=scheduled_date,
                    planned_intensity=plan["planned_intensity"],
                    duration_minutes=plan["duration_minutes"],
                    notes=plan["notes"],
                ),
            )
            session_id = str(new_session.id)
        else:
            existing.notes = f"{existing.notes or ''}\nAI replanning note: {plan['notes']}".strip()
            session_id = str(existing.id)

        if replanning_output.memory_to_write:
            self.memory_agent.write(
                user_id=str(user.id),
                text=replanning_output.memory_to_write,
                metadata={"category": "adherence", "source_event_id": str(source_event_id), "importance": 0.9},
            )

        self.events.emit(
            user_id=user.id,
            event_type=PLAN_REPLANNED,
            payload={"source_event_id": str(source_event_id), "session_id": session_id, "explanation": replanning_output.message},
        )

        return {"session_id": session_id, "explanation": replanning_output.message, "plan": plan}
