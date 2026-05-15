from __future__ import annotations

import random
from datetime import date, datetime, time, timedelta, timezone

from qdrant_client.http.models import FieldCondition, Filter, FilterSelector, MatchValue
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.ai.analytics.behavior_patterns import BehavioralPatternAnalyzer
from app.ai.analytics.predictors import PredictiveAnalyticsEngine
from app.ai.reports import AIWeeklyReport
from app.ai.memory.ingestion import MemoryIngestionPipeline
from app.ai.recommendations.candidate_generator import RecommendationCandidateGenerator
from app.ai.recommendations.ranker import RecommendationRanker
from app.core.qdrant_client import USER_MEMORY_COLLECTION, get_qdrant_client
from app.core.security import hash_password
from app.demo.profiles import DEMO_USERS, DemoUserProfile
from app.demo.simulation import DaySimulation, DemoBehaviorSimulator
from app.events.models import DomainEvent
from app.modules.auth.models import User
from app.modules.nutrition.models import Meal
from app.modules.recommendations.feedback_models import RecommendationFeedback
from app.modules.recommendations.models import Recommendation
from app.modules.recovery.models import RecoveryCheckin
from app.modules.sleep.models import SleepLog
from app.modules.users.models import UserProfile
from app.modules.workouts.models import WorkoutSession


class DemoDataSeeder:
    def __init__(self, db: Session, *, days: int = 180, seed: int = 42, reset: bool = True):
        self.db = db
        self.days = days
        self.seed = seed
        self.reset = reset
        self.random = random.Random(seed)
        self.memory_ingestion = MemoryIngestionPipeline()
        self.candidates = RecommendationCandidateGenerator()
        self.ranker = RecommendationRanker()

    def run(self) -> list[dict]:
        if self.reset:
            self.reset_demo_users()

        summaries = []
        for index, profile in enumerate(DEMO_USERS):
            if not self.reset and self._demo_user_exists(profile.email):
                summaries.append({"email": profile.email, "password": profile.password, "days_seeded": 0, "persona": profile.persona, "skipped": True})
                continue
            user = self._create_user(profile)
            simulations = DemoBehaviorSimulator(profile=profile, days=self.days, seed=self.seed + index * 101).simulate()
            self._write_history(user=user, profile=profile, simulations=simulations)
            self._write_behavior_memories(user=user, profile=profile, simulations=simulations)
            self._write_weekly_reports(user=user, simulations=simulations)
            self.db.commit()
            summaries.append({"email": user.email, "password": profile.password, "days_seeded": self.days, "persona": profile.persona})

        return summaries

    def _demo_user_exists(self, email: str) -> bool:
        return self.db.scalar(select(User).where(User.email == email)) is not None

    def reset_demo_users(self) -> None:
        demo_emails = [profile.email for profile in DEMO_USERS]
        users = list(self.db.scalars(select(User).where(User.email.in_(demo_emails))))
        for user in users:
            self._delete_qdrant_memories(str(user.id))
            self.db.delete(user)
        self.db.commit()

    def _create_user(self, profile: DemoUserProfile) -> User:
        user = User(
            email=profile.email,
            full_name=profile.full_name,
            hashed_password=hash_password(profile.password),
            is_active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=self.days + 12),
        )
        self.db.add(user)
        self.db.flush()
        self.db.add(
            UserProfile(
                user_id=user.id,
                primary_goal=profile.goal,
                fitness_level=profile.fitness_level,
                preferred_training_days=profile.training_days,
                preferred_unit="metric",
                onboarding_complete=True,
            )
        )
        self.db.flush()
        return user

    def _write_history(self, *, user: User, profile: DemoUserProfile, simulations: list[DaySimulation]) -> None:
        for simulation in simulations:
            workout = self._write_workout(user=user, simulation=simulation)
            self._write_meals(user=user, simulation=simulation)
            self._write_sleep(user=user, simulation=simulation)
            self._write_recovery(user=user, simulation=simulation)
            events, event_memory_ids = self._write_events(user=user, simulation=simulation, workout=workout)
            self._write_event_recommendations(user=user, events=events, simulation=simulation, event_memory_ids=event_memory_ids)

            if workout and workout.status == "missed" and self.random.random() < 0.42:
                self._write_historical_replan(user=user, missed_workout=workout, simulation=simulation)

    def _write_workout(self, *, user: User, simulation: DaySimulation) -> WorkoutSession | None:
        if not simulation.workout:
            return None
        workout = WorkoutSession(user_id=user.id, **simulation.workout)
        created_at = datetime.combine(simulation.day, time(hour=6), timezone.utc)
        workout.created_at = created_at
        workout.updated_at = created_at
        self.db.add(workout)
        self.db.flush()
        return workout

    def _write_meals(self, *, user: User, simulation: DaySimulation) -> None:
        for meal_payload in simulation.meals:
            meal = Meal(user_id=user.id, **meal_payload)
            meal.created_at = meal_payload["logged_at"]
            self.db.add(meal)
        self.db.flush()

    def _write_sleep(self, *, user: User, simulation: DaySimulation) -> None:
        sleep = SleepLog(user_id=user.id, **simulation.sleep)
        sleep.created_at = datetime.combine(simulation.day, time(hour=7), timezone.utc)
        self.db.add(sleep)
        self.db.flush()

    def _write_recovery(self, *, user: User, simulation: DaySimulation) -> None:
        recovery = RecoveryCheckin(user_id=user.id, **simulation.recovery)
        recovery.created_at = datetime.combine(simulation.day, time(hour=7, minute=20), timezone.utc)
        self.db.add(recovery)
        self.db.flush()

    def _write_events(self, *, user: User, simulation: DaySimulation, workout: WorkoutSession | None) -> tuple[list[DomainEvent], dict[str, list[str]]]:
        rows = []
        event_memory_ids = {}
        for event_payload in simulation.events:
            payload = dict(event_payload["payload"])
            if workout and event_payload["event_type"].startswith("workout."):
                payload["session_id"] = str(workout.id)
            event = DomainEvent(
                user_id=user.id,
                event_type=event_payload["event_type"],
                payload=payload,
                processed=True,
                created_at=datetime.combine(simulation.day, time(hour=21), timezone.utc),
            )
            self.db.add(event)
            self.db.flush()
            rows.append(event)

            memory_text = self._notable_event_memory(event)
            if memory_text:
                event_memory_ids[str(event.id)] = self.memory_ingestion.ingest_event(
                    user_id=str(user.id),
                    event_type=event.event_type,
                    text=memory_text,
                    metadata={
                        "category": self._event_category(event.event_type),
                        "source": "demo_historical_event",
                        "source_event_id": str(event.id),
                        "importance": self._event_importance(event.event_type),
                    },
                )
        return rows, event_memory_ids

    def _write_event_recommendations(
        self,
        *,
        user: User,
        events: list[DomainEvent],
        simulation: DaySimulation,
        event_memory_ids: dict[str, list[str]],
    ) -> None:
        dashboard_context = self._dashboard_like_context(simulation)
        for event in events:
            if event.event_type not in {"workout.missed", "sleep.poor", "recovery.low", "meal.logged"}:
                continue
            ranked = self.ranker.rank(
                self.candidates.generate_for_event(event_type=event.event_type, context={"dashboard": dashboard_context}),
                context={"dashboard": dashboard_context},
            )
            for candidate in ranked[:1]:
                recommendation = Recommendation(
                    user_id=user.id,
                    title=candidate["title"],
                    body=candidate["body"],
                    category=candidate["category"],
                    priority=candidate["priority"],
                    source_event_type=event.event_type,
                    confidence_score=candidate.get("confidence_score", 0.65),
                    reasoning_summary=candidate.get("reasoning_summary"),
                    triggering_factors=candidate.get("triggering_factors", [event.event_type]),
                    related_memory_ids=event_memory_ids.get(str(event.id), []),
                    status=self._historical_recommendation_status(event.event_type),
                    created_at=event.created_at + timedelta(minutes=5),
                )
                self.db.add(recommendation)
                self.db.flush()
                self.db.add(
                    DomainEvent(
                        user_id=user.id,
                        event_type="recommendation.generated",
                        payload={"recommendation_id": str(recommendation.id), "source_event_type": event.event_type},
                        processed=True,
                        created_at=recommendation.created_at,
                    )
                )
                if recommendation.status in {"accepted", "dismissed"}:
                    self.db.add(
                        RecommendationFeedback(
                            recommendation_id=recommendation.id,
                            user_id=user.id,
                            feedback_type=recommendation.status,
                            notes=self._feedback_note(recommendation.status),
                            created_at=recommendation.created_at + timedelta(hours=2),
                        )
                    )

    def _write_historical_replan(self, *, user: User, missed_workout: WorkoutSession, simulation: DaySimulation) -> None:
        replan_day = simulation.day + timedelta(days=1)
        if replan_day > date.today():
            return

        replacement = WorkoutSession(
            user_id=user.id,
            title=f"Adjusted {missed_workout.title}",
            scheduled_date=replan_day,
            status="completed" if self.random.random() < 0.65 else "scheduled",
            planned_intensity="low" if simulation.recovery["readiness_score"] < 55 else "moderate",
            duration_minutes=max(25, missed_workout.duration_minutes - 15),
            notes="Historical AI replan after missed session.",
            completed_at=datetime.combine(replan_day, time(hour=18), timezone.utc) if self.random.random() < 0.65 else None,
            created_at=datetime.combine(simulation.day, time(hour=22), timezone.utc),
            updated_at=datetime.combine(simulation.day, time(hour=22), timezone.utc),
        )
        self.db.add(replacement)
        self.db.flush()
        self.db.add(
            DomainEvent(
                user_id=user.id,
                event_type="plan.replanned",
                payload={
                    "source_session_id": str(missed_workout.id),
                    "session_id": str(replacement.id),
                    "explanation": "Historical AI replan created a shorter replacement session.",
                },
                processed=True,
                created_at=datetime.combine(simulation.day, time(hour=22, minute=5), timezone.utc),
            )
        )

    def _write_behavior_memories(self, *, user: User, profile: DemoUserProfile, simulations: list[DaySimulation]) -> None:
        completed = sum(1 for day in simulations if day.workout and day.workout["status"] == "completed")
        missed = sum(1 for day in simulations if day.workout and day.workout["status"] == "missed")
        low_recovery = sum(1 for day in simulations if day.recovery["readiness_score"] < 55)
        poor_sleep = sum(1 for day in simulations if day.sleep["duration_hours"] < 6 or day.sleep["quality_score"] < 55)
        avg_sleep = round(sum(day.sleep["duration_hours"] for day in simulations) / len(simulations), 2)

        memory_templates = [
            (
                f"{profile.full_name} behaves like a {profile.persona}. Over {self.days} days, completed {completed} workouts and missed {missed}.",
                "adherence",
                0.92,
            ),
            (
                f"Sleep pattern summary: average sleep is {avg_sleep} hours with {poor_sleep} poor sleep events.",
                "sleep",
                0.86,
            ),
            (
                f"Recovery observation: {low_recovery} low-readiness days. Fatigue trigger profile is {profile.fatigue_bias}.",
                "recovery",
                0.88,
            ),
            (
                f"Motivational trigger: {self._motivation_trigger(profile)} works best for {profile.full_name}.",
                "adherence",
                0.84,
            ),
            (
                f"Nutrition habit: meal consistency is {profile.meal_consistency}; goal is {profile.goal}.",
                "nutrition",
                0.78,
            ),
        ]

        for text, category, importance in memory_templates:
            self.memory_ingestion.ingest_event(
                user_id=str(user.id),
                event_type="demo.memory_seeded",
                text=text,
                metadata={"category": category, "source": "demo_seed", "importance": importance},
            )

    def _write_weekly_reports(self, *, user: User, simulations: list[DaySimulation]) -> None:
        by_week = {}
        for simulation in simulations:
            week_start = simulation.day - timedelta(days=simulation.day.weekday())
            by_week.setdefault(week_start, []).append(simulation)

        for week_start, week_days in sorted(by_week.items()):
            week_end = week_start + timedelta(days=6)
            completed = sum(1 for item in week_days if item.workout and item.workout["status"] == "completed")
            missed = sum(1 for item in week_days if item.workout and item.workout["status"] == "missed")
            avg_readiness = round(sum(item.recovery["readiness_score"] for item in week_days) / len(week_days), 1)
            avg_sleep = round(sum(item.sleep["duration_hours"] for item in week_days) / len(week_days), 2)
            calories = [sum(meal["calories"] for meal in item.meals) for item in week_days]
            avg_calories = round(sum(calories) / len(calories)) if calories else 0
            completion_rate = completed / max(completed + missed, 1)
            adherence_risk = max(0.05, min(0.95, 0.55 - completion_rate * 0.35 + missed * 0.08 + (0.12 if avg_sleep < 6.2 else 0)))
            recovery_decline = max(0.05, min(0.95, 0.25 + (0.25 if avg_readiness < 60 else 0) + (0.12 if avg_sleep < 6.2 else 0)))
            summary = (
                f"Weekly AI review: completed {completed} workouts and missed {missed}. "
                f"Average readiness was {avg_readiness}, average sleep was {avg_sleep}h, and average calories logged were {avg_calories}. "
                f"Adherence risk is {'high' if adherence_risk > 0.7 else 'medium' if adherence_risk > 0.4 else 'low'}."
            )
            self.db.add(
                AIWeeklyReport(
                    user_id=user.id,
                    week_start=week_start,
                    week_end=week_end,
                    summary=summary,
                    metrics={
                        "completed_workouts": completed,
                        "missed_workouts": missed,
                        "average_readiness": avg_readiness,
                        "average_sleep_hours": avg_sleep,
                        "average_calories": avg_calories,
                    },
                    predictions={
                        "adherence_risk": {"score": round(adherence_risk, 3), "level": self._risk_level(adherence_risk)},
                        "recovery_decline": {"score": round(recovery_decline, 3), "level": self._risk_level(recovery_decline)},
                    },
                    created_at=datetime.combine(min(week_end, date.today()), time(hour=20), timezone.utc),
                )
            )
        self.db.flush()

    def _notable_event_memory(self, event: DomainEvent) -> str | None:
        payload = event.payload or {}
        if event.event_type == "workout.missed":
            return f"Historical missed workout. Session was {payload.get('title', 'unknown')} with {payload.get('planned_intensity', 'unknown')} planned intensity."
        if event.event_type == "sleep.poor":
            return f"Historical poor sleep: {payload.get('duration_hours')} hours and quality {payload.get('quality_score')}."
        if event.event_type == "recovery.low":
            return f"Historical low recovery day with readiness {payload.get('readiness')}."
        if event.event_type == "workout.completed" and self.random.random() < 0.08:
            return f"Historical workout completed: {payload.get('title', 'training session')}."
        return None

    def _event_category(self, event_type: str) -> str:
        if event_type.startswith("workout"):
            return "workout" if event_type == "workout.completed" else "adherence"
        if event_type.startswith("sleep"):
            return "sleep"
        if event_type.startswith("recovery"):
            return "recovery"
        return "adherence"

    def _event_importance(self, event_type: str) -> float:
        if event_type in {"workout.missed", "recovery.low", "sleep.poor"}:
            return 0.86
        return 0.58

    def _risk_level(self, value: float) -> str:
        if value > 0.7:
            return "high"
        if value > 0.4:
            return "medium"
        return "low"

    def _dashboard_like_context(self, simulation: DaySimulation) -> dict:
        calories = sum(meal["calories"] for meal in simulation.meals)
        protein = round(sum(meal["protein_g"] for meal in simulation.meals), 1)
        return {
            "readiness_score": simulation.recovery["readiness_score"],
            "today_workout": simulation.workout or {},
            "nutrition": {
                "calories": calories,
                "protein_g": protein,
                "calorie_target": 2200,
                "protein_target_g": 150,
            },
        }

    def _historical_recommendation_status(self, event_type: str) -> str:
        if event_type == "workout.missed":
            return "accepted" if self.random.random() < 0.56 else "dismissed"
        if event_type in {"sleep.poor", "recovery.low"}:
            return "accepted" if self.random.random() < 0.68 else "active"
        return "accepted" if self.random.random() < 0.42 else "dismissed"

    def _feedback_note(self, status: str) -> str:
        if status == "accepted":
            return self.random.choice(["Helpful and realistic.", "Matched my schedule.", "Good smaller next step."])
        return self.random.choice(["Not useful today.", "Timing was off.", "Already handled this."])

    def _motivation_trigger(self, profile: DemoUserProfile) -> str:
        mapping = {
            "highly_consistent_athlete": "performance streaks and progression feedback",
            "beginner_weight_loss_user": "simple calorie and walking wins",
            "adherence_struggles": "small minimum sessions and non-shaming recovery plans",
            "poor_sleep_high_fatigue": "readiness-aware training adjustments",
            "muscle_gain_focused": "volume progression and protein consistency",
        }
        return mapping[profile.persona]

    def _delete_qdrant_memories(self, user_id: str) -> None:
        try:
            get_qdrant_client().delete(
                collection_name=USER_MEMORY_COLLECTION,
                points_selector=FilterSelector(
                    filter=Filter(must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))])
                ),
            )
        except Exception:
            # Qdrant may not be running when a developer only wants to reset Postgres.
            pass
