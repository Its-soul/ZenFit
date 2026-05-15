import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.memory.ingestion import MemoryIngestionPipeline
from app.ai.observability import AILogger
from app.ai.pipelines.adaptive_replanning_pipeline import AdaptiveReplanningPipeline
from app.ai.recommendations.candidate_generator import RecommendationCandidateGenerator
from app.ai.recommendations.ranker import RecommendationRanker
from app.events.event_bus import RedisEventBus
from app.events.event_types import (
    ADHERENCE_LOW,
    MEAL_LOGGED,
    PLAN_REPLANNED,
    RECOMMENDATION_GENERATED,
    RECOVERY_LOW,
    SLEEP_LOGGED,
    SLEEP_POOR,
    WORKOUT_COMPLETED,
    WORKOUT_MISSED,
    WORKOUT_RESCHEDULED,
)
from app.events.models import DomainEvent
from app.events.producer import EventProducer
from app.modules.auth.repository import UserRepository
from app.modules.dashboard.service import DashboardService
from app.modules.recommendations.repository import RecommendationRepository

logger = logging.getLogger(__name__)


class AIEventHandler:
    def __init__(self, db: Session):
        self.db = db
        self.memory_ingestion = MemoryIngestionPipeline()
        self.candidates = RecommendationCandidateGenerator()
        self.ranker = RecommendationRanker()
        self.recommendations = RecommendationRepository(db)
        self.events = EventProducer(db)
        self.realtime = RedisEventBus()

    def handle(self, event: DomainEvent) -> None:
        user = UserRepository(self.db).get_by_id(event.user_id)
        if user is None:
            logger.warning("Skipping event for missing user: %s", event.id)
            return

        dashboard = DashboardService(self.db).today(user).model_dump(mode="json")
        memory_text, category, importance = self._memory_text(event, dashboard)
        memory_ids = self.memory_ingestion.ingest_event(
            user_id=str(event.user_id),
            event_type=event.event_type,
            text=memory_text,
            metadata={"category": category, "source_event_id": str(event.id), "importance": importance},
        )

        replanning_result = None
        if event.event_type == WORKOUT_MISSED:
            replanning_result = AdaptiveReplanningPipeline(self.db).run_for_missed_workout(user=user, source_event_id=event.id)
            self.events.emit(
                user_id=user.id,
                event_type=ADHERENCE_LOW,
                payload={"source_event_id": str(event.id), "reason": "missed_workout"},
            )
            dashboard = DashboardService(self.db).today(user).model_dump(mode="json")

        generated = self._generate_recommendations(event=event, dashboard=dashboard, memory_ids=memory_ids)

        event.processed = True
        AILogger(self.db).log(
            operation="event_ai_pipeline",
            user_id=event.user_id,
            agent_name="AIEventHandler",
            input_summary=f"Processed {event.event_type}",
            output_summary=f"Generated {len(generated)} recommendations",
            retrieved_memory_ids=memory_ids,
            scores={"recommendation_count": len(generated)},
        )
        self.db.commit()

        self._publish_dashboard_update(
            user_id=str(event.user_id),
            event=event,
            memory_ids=memory_ids,
            recommendations=generated,
            replanning_result=replanning_result,
        )

    def _memory_text(self, event: DomainEvent, dashboard: dict) -> tuple[str, str, float]:
        payload = event.payload or {}

        if event.event_type == WORKOUT_MISSED:
            return (
                f"User missed a workout. Planned intensity was {payload.get('planned_intensity', 'unknown')}. This may indicate adherence friction or schedule conflict.",
                "adherence",
                0.9,
            )
        if event.event_type == WORKOUT_COMPLETED:
            return ("User completed a workout, strengthening recent workout consistency.", "workout", 0.7)
        if event.event_type == WORKOUT_RESCHEDULED:
            return (
                f"User rescheduled a workout from {payload.get('from_date')} to {payload.get('to_date')}. Reason: {payload.get('reason') or 'not provided'}.",
                "adherence",
                0.72,
            )
        if event.event_type == MEAL_LOGGED:
            nutrition = dashboard.get("nutrition", {})
            return (
                f"User logged a meal. Daily intake is now {nutrition.get('calories', 0)} calories and {nutrition.get('protein_g', 0)}g protein.",
                "nutrition",
                0.55,
            )
        if event.event_type == SLEEP_LOGGED:
            return ("User logged sleep data, improving recovery context.", "sleep", 0.55)
        if event.event_type == SLEEP_POOR:
            return (
                f"Poor sleep detected: {payload.get('duration_hours')} hours and quality {payload.get('quality_score')}.",
                "sleep",
                0.85,
            )
        if event.event_type == RECOVERY_LOW:
            return (f"Low readiness detected with score {payload.get('readiness')}.", "recovery", 0.9)
        if event.event_type == PLAN_REPLANNED:
            return (f"AI replanned the user's plan: {payload.get('explanation')}", "adherence", 0.8)
        if event.event_type == ADHERENCE_LOW:
            return ("Adherence risk increased after a missed workout or incomplete routine signal.", "adherence", 0.85)
        if event.event_type == RECOMMENDATION_GENERATED:
            return ("AI generated a recommendation from recent user behavior and system context.", "recommendation", 0.45)

        return (f"Fitness event recorded: {event.event_type}", "adherence", 0.4)

    def _generate_recommendations(self, *, event: DomainEvent, dashboard: dict, memory_ids: list[str]) -> list[dict]:
        if event.event_type == RECOMMENDATION_GENERATED:
            return []

        ranked = self.ranker.rank(
            self.candidates.generate_for_event(event_type=event.event_type, context={"dashboard": dashboard}),
            context={"dashboard": dashboard},
        )
        created = []
        for candidate in ranked[:2]:
            recommendation = self.recommendations.create(
                user_id=event.user_id,
                title=candidate["title"],
                body=candidate["body"],
                category=candidate["category"],
                priority=candidate["priority"],
                source_event_type=event.event_type,
                confidence_score=candidate.get("confidence_score", candidate.get("score", 0.6)),
                reasoning_summary=candidate.get("reasoning_summary"),
                triggering_factors=candidate.get("triggering_factors", [event.event_type]),
                related_memory_ids=memory_ids,
            )
            created.append(
                {
                    "id": str(recommendation.id),
                    "title": recommendation.title,
                    "body": recommendation.body,
                    "category": recommendation.category,
                    "priority": recommendation.priority,
                    "confidence_score": recommendation.confidence_score,
                    "reasoning_summary": recommendation.reasoning_summary,
                    "triggering_factors": recommendation.triggering_factors,
                    "related_memory_ids": recommendation.related_memory_ids,
                }
            )
            if not getattr(recommendation, "_was_merged", False):
                self.events.emit(
                    user_id=event.user_id,
                    event_type=RECOMMENDATION_GENERATED,
                    payload={"recommendation_id": str(recommendation.id), "source_event_type": event.event_type},
                )
        return created

    def _publish_dashboard_update(
        self,
        *,
        user_id: str,
        event: DomainEvent,
        memory_ids: list[str],
        recommendations: list[dict],
        replanning_result: dict | None,
    ) -> None:
        payload = {
            "source_event": event.event_type,
            "memory_ids": memory_ids,
            "recommendations": recommendations,
            "replanning": replanning_result,
        }
        self.realtime.publish_realtime(user_id=user_id, event_type="ai.event.processed", payload=payload)
