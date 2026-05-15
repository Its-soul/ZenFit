# Adaptive AI Fitness Operating System Architecture

## 0. Product Definition

This product is an AI-first adaptive fitness operating system. It is not a passive tracker. It observes user behavior, stores long-term memory, reacts to events, updates plans, predicts adherence risk, and proactively coaches the user across workouts, nutrition, recovery, sleep, planning, and habit formation.

Core product promise:

```text
Personalized fitness guidance that adapts every day based on behavior, readiness, adherence, nutrition, sleep, goals, and user context.
```

Core design goals:

- Premium SaaS frontend with simple beginner-manageable structure.
- Feature-first FastAPI backend.
- AI-first services with clear agents, tools, prompts, memory, pipelines, and evaluation.
- Event-driven intelligence for proactive replanning.
- Easy debugging, interviewing, onboarding, and AI coding-agent collaboration.
- Kubernetes-ready without forcing unnecessary microservices on day one.

Recommended initial architecture:

```text
Modular monorepo
FastAPI modular backend
Python AI service package inside backend
PostgreSQL for source-of-truth data
Qdrant for semantic memory
Redis for cache, realtime state, and event queues
Next.js frontend with simple route-focused organization
Docker Compose for local development
Kubernetes manifests prepared for production
```

---

## 1. Complete Production-Level Folder Structure

```text
ai-fitness-os/
|
|-- README.md
|-- .env.example
|-- .gitignore
|-- docker-compose.yml
|-- Makefile
|-- package.json
|
|-- docs/
|   |-- architecture.md
|   |-- api-contracts.md
|   |-- ai-agents.md
|   |-- event-flows.md
|   |-- database-schema.md
|   |-- deployment.md
|   |-- onboarding.md
|
|-- frontend/
|   |-- package.json
|   |-- next.config.js
|   |-- postcss.config.js
|   |-- tailwind.config.js
|   |-- jsconfig.json
|   |-- .env.example
|   |
|   |-- app/
|   |   |-- layout.js
|   |   |-- page.js
|   |   |-- globals.css
|   |   |-- loading.js
|   |   |-- error.js
|   |   |
|   |   |-- auth/
|   |   |   |-- login/page.js
|   |   |   |-- register/page.js
|   |   |
|   |   |-- dashboard/
|   |   |   |-- page.js
|   |   |
|   |   |-- workouts/
|   |   |   |-- page.js
|   |   |   |-- [planId]/page.js
|   |   |
|   |   |-- nutrition/
|   |   |   |-- page.js
|   |   |   |-- meal-analysis/page.js
|   |   |
|   |   |-- recovery/
|   |   |   |-- page.js
|   |   |
|   |   |-- sleep/
|   |   |   |-- page.js
|   |   |
|   |   |-- coach/
|   |   |   |-- page.js
|   |   |
|   |   |-- analytics/
|   |   |   |-- page.js
|   |   |
|   |   |-- settings/
|   |       |-- page.js
|   |
|   |-- components/
|   |   |-- ui/
|   |   |-- layout/
|   |   |   |-- AppShell.js
|   |   |   |-- Sidebar.js
|   |   |   |-- Topbar.js
|   |   |   |-- MobileNav.js
|   |   |
|   |   |-- common/
|   |   |   |-- GlassPanel.js
|   |   |   |-- MetricCard.js
|   |   |   |-- EmptyState.js
|   |   |   |-- LoadingState.js
|   |   |   |-- ErrorState.js
|   |   |
|   |   |-- charts/
|   |   |   |-- TrendLine.js
|   |   |   |-- DonutScore.js
|   |   |   |-- HeatmapGrid.js
|   |   |
|   |   |-- ai/
|   |       |-- CoachChat.js
|   |       |-- AIInsightCard.js
|   |       |-- RecommendationCard.js
|   |       |-- PlanChangeTimeline.js
|   |
|   |-- features/
|   |   |-- auth/
|   |   |   |-- components/
|   |   |   |-- hooks/
|   |   |   |-- services.js
|   |   |
|   |   |-- dashboard/
|   |   |   |-- components/
|   |   |   |-- hooks/
|   |   |
|   |   |-- workouts/
|   |   |   |-- components/
|   |   |   |-- hooks/
|   |   |   |-- services.js
|   |   |
|   |   |-- nutrition/
|   |   |-- recovery/
|   |   |-- sleep/
|   |   |-- coach/
|   |   |-- analytics/
|   |   |-- recommendations/
|   |
|   |-- services/
|   |   |-- apiClient.js
|   |   |-- authService.js
|   |   |-- workoutService.js
|   |   |-- nutritionService.js
|   |   |-- aiCoachService.js
|   |   |-- websocketService.js
|   |
|   |-- hooks/
|   |   |-- useAuth.js
|   |   |-- useApi.js
|   |   |-- useWebSocket.js
|   |   |-- useRealtimeDashboard.js
|   |
|   |-- lib/
|   |   |-- constants.js
|   |   |-- routes.js
|   |   |-- animations.js
|   |   |-- theme.js
|   |
|   |-- utils/
|   |   |-- formatDate.js
|   |   |-- formatNumber.js
|   |   |-- scoreColor.js
|   |
|   |-- styles/
|   |   |-- glass.css
|   |   |-- animations.css
|   |
|   |-- public/
|       |-- images/
|       |-- icons/
|
|-- backend/
|   |-- pyproject.toml
|   |-- requirements.txt
|   |-- alembic.ini
|   |-- Dockerfile
|   |-- .env.example
|   |
|   |-- app/
|   |   |-- main.py
|   |   |-- config.py
|   |   |-- dependencies.py
|   |   |-- exceptions.py
|   |   |
|   |   |-- core/
|   |   |   |-- security.py
|   |   |   |-- logging.py
|   |   |   |-- middleware.py
|   |   |   |-- permissions.py
|   |   |   |-- rate_limits.py
|   |   |
|   |   |-- db/
|   |   |   |-- session.py
|   |   |   |-- base.py
|   |   |   |-- migrations/
|   |   |
|   |   |-- modules/
|   |   |   |-- auth/
|   |   |   |   |-- routes.py
|   |   |   |   |-- schemas.py
|   |   |   |   |-- models.py
|   |   |   |   |-- repository.py
|   |   |   |   |-- service.py
|   |   |   |   |-- tests/
|   |   |   |
|   |   |   |-- users/
|   |   |   |-- workouts/
|   |   |   |   |-- routes.py
|   |   |   |   |-- schemas.py
|   |   |   |   |-- models.py
|   |   |   |   |-- repository.py
|   |   |   |   |-- service.py
|   |   |   |   |-- ai_logic.py
|   |   |   |   |-- prompts/
|   |   |   |   |-- pipelines/
|   |   |   |   |-- tests/
|   |   |   |
|   |   |   |-- nutrition/
|   |   |   |-- recovery/
|   |   |   |-- sleep/
|   |   |   |-- analytics/
|   |   |   |-- ai_coach/
|   |   |   |-- recommendations/
|   |   |   |-- replanning/
|   |   |   |-- adherence/
|   |   |   |-- notifications/
|   |   |   |-- uploads/
|   |   |
|   |   |-- ai/
|   |   |   |-- README.md
|   |   |   |-- agents/
|   |   |   |   |-- base_agent.py
|   |   |   |   |-- planner_agent.py
|   |   |   |   |-- replanning_agent.py
|   |   |   |   |-- nutrition_agent.py
|   |   |   |   |-- recovery_agent.py
|   |   |   |   |-- coach_agent.py
|   |   |   |   |-- analytics_agent.py
|   |   |   |   |-- recommendation_agent.py
|   |   |   |   |-- memory_agent.py
|   |   |   |
|   |   |   |-- orchestrators/
|   |   |   |   |-- agent_router.py
|   |   |   |   |-- planning_orchestrator.py
|   |   |   |   |-- coaching_orchestrator.py
|   |   |   |   |-- event_orchestrator.py
|   |   |   |
|   |   |   |-- memory/
|   |   |   |   |-- ingestion.py
|   |   |   |   |-- chunking.py
|   |   |   |   |-- embeddings.py
|   |   |   |   |-- vector_store.py
|   |   |   |   |-- retriever.py
|   |   |   |   |-- reranker.py
|   |   |   |   |-- context_builder.py
|   |   |   |   |-- memory_writer.py
|   |   |   |
|   |   |   |-- tools/
|   |   |   |   |-- workout_tools.py
|   |   |   |   |-- nutrition_tools.py
|   |   |   |   |-- analytics_tools.py
|   |   |   |   |-- memory_tools.py
|   |   |   |   |-- scheduler_tools.py
|   |   |   |   |-- notification_tools.py
|   |   |   |
|   |   |   |-- prompts/
|   |   |   |   |-- planner.md
|   |   |   |   |-- replanning.md
|   |   |   |   |-- nutrition.md
|   |   |   |   |-- recovery.md
|   |   |   |   |-- coach.md
|   |   |   |   |-- analytics.md
|   |   |   |   |-- recommendation.md
|   |   |   |
|   |   |   |-- pipelines/
|   |   |   |   |-- missed_workout_pipeline.py
|   |   |   |   |-- meal_analysis_pipeline.py
|   |   |   |   |-- coaching_pipeline.py
|   |   |   |   |-- weekly_report_pipeline.py
|   |   |   |   |-- adaptive_plan_pipeline.py
|   |   |   |
|   |   |   |-- recommendations/
|   |   |   |   |-- rules_engine.py
|   |   |   |   |-- scoring.py
|   |   |   |   |-- candidate_generator.py
|   |   |   |   |-- ranker.py
|   |   |   |
|   |   |   |-- analytics/
|   |   |   |   |-- adherence_predictor.py
|   |   |   |   |-- readiness_model.py
|   |   |   |   |-- trend_detector.py
|   |   |   |   |-- report_generator.py
|   |   |   |
|   |   |   |-- evaluation/
|   |   |   |   |-- datasets/
|   |   |   |   |-- prompt_tests.py
|   |   |   |   |-- retrieval_tests.py
|   |   |   |   |-- agent_eval.py
|   |   |   |   |-- safety_eval.py
|   |   |   |
|   |   |   |-- training/
|   |   |       |-- notebooks/
|   |   |       |-- datasets/
|   |   |       |-- feature_builders/
|   |   |       |-- model_registry.py
|   |   |
|   |   |-- events/
|   |   |   |-- event_types.py
|   |   |   |-- event_bus.py
|   |   |   |-- producers.py
|   |   |   |-- consumers.py
|   |   |   |-- handlers/
|   |   |       |-- workout_events.py
|   |   |       |-- nutrition_events.py
|   |   |       |-- recovery_events.py
|   |   |       |-- adherence_events.py
|   |   |
|   |   |-- realtime/
|   |   |   |-- websocket_manager.py
|   |   |   |-- channels.py
|   |   |   |-- serializers.py
|   |   |
|   |   |-- storage/
|   |   |   |-- s3_client.py
|   |   |   |-- upload_service.py
|   |   |
|   |   |-- tasks/
|   |       |-- worker.py
|   |       |-- scheduled_jobs.py
|   |
|   |-- tests/
|       |-- conftest.py
|       |-- integration/
|       |-- e2e/
|
|-- infra/
|   |-- docker/
|   |   |-- frontend.Dockerfile
|   |   |-- backend.Dockerfile
|   |   |-- worker.Dockerfile
|   |
|   |-- k8s/
|   |   |-- base/
|   |   |   |-- namespace.yaml
|   |   |   |-- configmap.yaml
|   |   |   |-- secrets.example.yaml
|   |   |   |-- frontend-deployment.yaml
|   |   |   |-- backend-deployment.yaml
|   |   |   |-- worker-deployment.yaml
|   |   |   |-- redis-deployment.yaml
|   |   |   |-- qdrant-deployment.yaml
|   |   |   |-- ingress.yaml
|   |   |
|   |   |-- overlays/
|   |       |-- dev/
|   |       |-- staging/
|   |       |-- production/
|   |
|   |-- monitoring/
|       |-- prometheus/
|       |-- grafana/
|       |-- loki/
|
|-- scripts/
|   |-- dev.sh
|   |-- seed_db.py
|   |-- create_admin.py
|   |-- run_migrations.sh
|   |-- evaluate_ai.py
|
|-- data/
    |-- seed/
    |-- sample_uploads/
```

---

## 2. Major Folder Responsibilities

| Folder | Responsibility |
|---|---|
| `frontend/` | Next.js App Router UI, route pages, feature components, API clients, simple hooks. |
| `backend/app/modules/` | Business features. Each feature owns its API, schemas, models, repository, service, AI hooks, and tests. |
| `backend/app/ai/` | AI-native layer: agents, prompts, memory, tools, orchestration, recommendations, analytics, evaluation. |
| `backend/app/events/` | Event definitions, publishing, consumption, and AI-triggering handlers. |
| `backend/app/realtime/` | WebSocket connection management and live dashboard updates. |
| `backend/app/storage/` | S3 upload and file access logic. |
| `infra/` | Docker, Kubernetes, and monitoring assets. |
| `docs/` | Human-readable architecture, onboarding, event flows, API contracts, and AI explanation docs. |
| `scripts/` | Developer automation and operational scripts. |

Rule of thumb:

```text
API endpoint -> module routes
Business rules -> module service
Database query -> module repository
AI reasoning -> app/ai
Prompt text -> app/ai/prompts
RAG retrieval -> app/ai/memory
Event reaction -> app/events/handlers
Realtime push -> app/realtime
```

---

## 3. Frontend Architecture

Frontend principles:

- Keep the frontend simple, route-focused, and easy to debug.
- No Redux, no microfrontends, no heavy state frameworks.
- Use server routes only where useful. Most app screens can be client components that call FastAPI through Axios.
- Use `features/` for domain-specific components.
- Use `components/` for reusable visual primitives.
- Use `services/` for all API calls.
- Use `hooks/` for repeated frontend behavior.

Visual direction:

- Dark premium SaaS interface.
- Glassmorphism panels over subtle depth backgrounds.
- Framer Motion for page transitions, metric card entrance, chat message streaming, and plan-change timelines.
- Shadcn UI for buttons, dialogs, tabs, sheets, dropdowns, forms, cards, inputs, and toasts.
- Tailwind CSS for layout and visual system.

Recommended route pages:

| Route | Purpose |
|---|---|
| `/dashboard` | Daily AI command center: readiness, next workout, calories, adherence risk, AI insights. |
| `/workouts` | Plans, sessions, exercise history, modifications. |
| `/nutrition` | Meals, macros, calorie targets, meal feedback. |
| `/nutrition/meal-analysis` | Meal upload and AI nutrition analysis. |
| `/recovery` | Readiness, fatigue, HRV, soreness, deload guidance. |
| `/sleep` | Sleep trends and recovery impact. |
| `/coach` | AI coach chat with memory and tool calling. |
| `/analytics` | Progress, adherence prediction, weekly reports. |
| `/settings` | Profile, goals, integrations, notifications. |

Frontend state strategy:

- Authentication state: `useAuth`.
- Remote data: lightweight custom hooks around Axios.
- Realtime dashboard data: `useWebSocket` and `useRealtimeDashboard`.
- Local UI state: React `useState`.
- Shared constants: `lib/constants.js`.
- API URLs and app routes: `lib/routes.js`.

Example frontend request pattern:

```javascript
// frontend/services/workoutService.js
import apiClient from "./apiClient";

export function getTodayWorkout() {
  return apiClient.get("/workouts/today");
}

export function completeWorkout(sessionId, payload) {
  return apiClient.post(`/workouts/sessions/${sessionId}/complete`, payload);
}
```

---

## 4. Backend Architecture

Backend style:

```text
Feature-first modular FastAPI architecture
```

Every feature module follows:

```text
routes.py       HTTP layer only
schemas.py      Pydantic request and response schemas
models.py       SQLAlchemy models
repository.py   Database access only
service.py      Business logic
ai_logic.py     Calls into app/ai when this feature needs intelligence
prompts/        Feature-specific prompt fragments if needed
pipelines/      Feature-specific pipeline wrappers if needed
tests/          Unit tests for this module
```

Example request flow:

```text
POST /workouts/sessions/{id}/complete
    -> workouts/routes.py
    -> workouts/service.py
    -> workouts/repository.py
    -> PostgreSQL update
    -> events/producers.py emits workout.completed
    -> Redis event queue
    -> events/handlers/workout_events.py
    -> AI memory ingestion and recommendation refresh
    -> realtime dashboard update
```

Backend module map:

| Module | Responsibility |
|---|---|
| `auth` | Login, registration, password hashing, JWT, refresh tokens. |
| `users` | Profile, goals, preferences, fitness level, constraints. |
| `workouts` | Exercises, plans, sessions, volume, completion, progression. |
| `nutrition` | Meals, calories, macros, meal analysis, food logs. |
| `recovery` | Readiness, fatigue, soreness, HRV, rest recommendations. |
| `sleep` | Sleep logs, duration, quality, trends. |
| `analytics` | Trend reports, adherence, progress metrics. |
| `ai_coach` | Chat endpoints and coaching sessions. |
| `recommendations` | User-facing recommendation APIs. |
| `replanning` | Plan adjustment APIs and replanning history. |
| `adherence` | Compliance scoring, missed behavior, risk prediction. |
| `notifications` | Push/email/in-app nudges. |
| `uploads` | Meal images and progress photos via S3. |

---

## 5. AI Architecture

AI layer responsibility:

```text
Turn user data and events into personalized plans, explanations, recommendations, and adaptive behavior.
```

The AI layer is intentionally separate from normal business modules so it is obvious where to debug model behavior.

AI folders:

| Folder | Purpose |
|---|---|
| `agents/` | Role-specific AI agents. Each agent has a narrow job. |
| `orchestrators/` | Decides which agents run, in what order, with what context. |
| `memory/` | RAG ingestion, embedding, retrieval, reranking, context assembly. |
| `tools/` | Tool-call functions agents can use to access system data. |
| `prompts/` | System prompts and role prompts. |
| `pipelines/` | End-to-end workflows like missed workout or meal analysis. |
| `recommendations/` | Candidate generation, scoring, ranking. |
| `analytics/` | Prediction models and trend detection. |
| `evaluation/` | Prompt tests, retrieval tests, safety tests, agent quality checks. |
| `training/` | Datasets, feature builders, experiments, model registry. |

Debugging map:

| Problem | Look Here |
|---|---|
| Bad AI answer | `ai/prompts`, `ai/orchestrators`, `ai/pipelines` |
| Missing context | `ai/memory/retriever.py`, `context_builder.py` |
| Wrong recommendations | `ai/recommendations/scoring.py`, `ranker.py` |
| Bad adherence prediction | `ai/analytics/adherence_predictor.py` |
| Hallucinated user facts | `ai/memory/context_builder.py`, prompt grounding rules |
| Tool called wrong data | `ai/tools/` and related module repositories |
| Event did not trigger AI | `events/handlers/` and `event_orchestrator.py` |

---

## 6. Multi-Agent System

Agents are not separate services at first. They are Python classes with shared interfaces. This keeps development manageable while still giving clean AI boundaries.

Base agent interface:

```text
AgentInput:
  user_id
  intent
  event
  current_state
  retrieved_memory
  available_tools

AgentOutput:
  summary
  reasoning_trace_for_logs
  actions
  recommendations
  user_facing_message
  confidence
```

Agents:

| Agent | Responsibility |
|---|---|
| Planner Agent | Creates workout plans, meal plans, weekly schedules, progression strategy. |
| Replanning Agent | Adjusts plans after missed sessions, poor sleep, fatigue, injuries, schedule changes. |
| Nutrition Agent | Analyzes meals, estimates calories/macros, suggests corrections. |
| Recovery Agent | Computes readiness from sleep, fatigue, soreness, HRV, workload. |
| Coach Agent | Conversational assistant, motivation, explanation, behavior support. |
| Analytics Agent | Weekly reports, progress trends, adherence prediction, risk detection. |
| Recommendation Agent | Personalized suggestions and habit optimization. |
| Memory Agent | Writes, retrieves, summarizes, and manages long-term user memory. |

Agent orchestration patterns:

```text
Single-agent flow:
  User asks direct nutrition question
  -> Coach orchestrator routes to Nutrition Agent
  -> Memory Agent retrieves context
  -> Nutrition Agent responds

Multi-agent flow:
  User misses workout after poor sleep
  -> Event Orchestrator
  -> Recovery Agent computes readiness
  -> Replanning Agent modifies workout plan
  -> Nutrition Agent adjusts calorie distribution if needed
  -> Recommendation Agent creates next-best actions
  -> Coach Agent explains changes
  -> Memory Agent writes behavioral event
```

---

## 7. RAG Memory System Flow

Memory is split into two types:

| Memory Type | Storage | Purpose |
|---|---|---|
| Structured memory | PostgreSQL | Accurate facts: workouts, meals, sleep, metrics, goals. |
| Semantic memory | Qdrant | Searchable behavior patterns, coaching notes, habit insights, summaries. |

Memory examples:

- Workout history.
- Skipped workouts.
- Meal habits.
- Adherence patterns.
- Motivational triggers.
- Sleep behavior.
- Fatigue trends.
- Nutrition consistency.
- Preferred workout times.
- Common barriers.

RAG ingestion flow:

```text
Domain event occurs
  -> event handler receives event
  -> memory ingestion builds memory record
  -> chunking creates compact semantic chunks
  -> embedding model creates vectors
  -> Qdrant stores vector with metadata
  -> PostgreSQL stores memory audit/reference row
```

RAG retrieval flow:

```text
AI request starts
  -> determine intent
  -> build retrieval query
  -> retrieve candidate memories from Qdrant
  -> rerank by relevance, recency, importance, safety
  -> fetch structured facts from PostgreSQL
  -> context builder assembles grounded context
  -> agent receives final context
```

Memory metadata:

```text
user_id
memory_type
source_event
timestamp
importance_score
confidence_score
privacy_scope
related_entity_id
tags
```

Context-building rule:

```text
Agents should answer from structured facts first, semantic memory second, and general model knowledge last.
```

---

## 8. Event-Driven Intelligence

Events make the AI proactive.

Important event types:

```text
workout.scheduled
workout.completed
workout.missed
workout.modified
meal.logged
meal.over_target
meal.under_protein
sleep.logged
sleep.poor
recovery.low_readiness
activity.inactive_day
adherence.risk_increased
plan.replanned
recommendation.generated
coach.message_sent
```

Event components:

| Component | Responsibility |
|---|---|
| `event_types.py` | Canonical event names and payload contracts. |
| `event_bus.py` | Publish and consume through Redis. |
| `producers.py` | Helper functions modules use to emit events. |
| `consumers.py` | Worker loops that process queued events. |
| `handlers/` | Event-specific business and AI reactions. |

Event payload example:

```json
{
  "event_id": "evt_123",
  "event_type": "workout.missed",
  "user_id": "user_456",
  "occurred_at": "2026-05-15T08:30:00Z",
  "source": "workouts",
  "data": {
    "session_id": "session_789",
    "planned_intensity": "moderate",
    "missed_reason": "not_reported"
  }
}
```

---

## 9. Required AI Pipeline Flows

### Missed Workout Flow

```text
User misses workout
  -> workout.missed event created
  -> Redis event queue
  -> workout event handler
  -> Event Orchestrator starts missed_workout_pipeline
  -> Memory Agent retrieves recent adherence, sleep, fatigue, schedule patterns
  -> Recovery Agent calculates readiness
  -> Replanning Agent decides whether to shift, reduce, combine, or skip volume
  -> Nutrition Agent checks calorie/protein adjustment needs
  -> Recommendation Agent creates next-best actions
  -> Coach Agent generates explanation
  -> PostgreSQL saves plan change and recommendation
  -> Qdrant stores memory summary
  -> WebSocket pushes dashboard update
```

### Meal Analysis Flow

```text
Meal image uploaded
  -> uploads module stores image in S3
  -> nutrition module creates meal_analysis job
  -> Nutrition Agent runs image interpretation pipeline
  -> food detection
  -> food classification
  -> portion estimation
  -> nutrition calculation
  -> compare against daily targets
  -> Recommendation Agent suggests correction
  -> Coach Agent creates user-friendly meal feedback
  -> meal.logged or meal.over_target event emitted
  -> dashboard updates in realtime
```

### Coaching Flow

```text
User asks question
  -> ai_coach route receives message
  -> Coaching Orchestrator classifies intent
  -> Memory Agent retrieves semantic memory
  -> Tool router selects allowed tools
  -> Agent calls structured tools if needed
  -> Context Builder assembles user state
  -> Coach Agent reasons with context
  -> Response generated with citations to user data where possible
  -> Conversation stored in PostgreSQL
  -> Important coaching insight stored in Qdrant
```

### Weekly Adaptive Plan Flow

```text
Scheduled weekly job
  -> Analytics Agent reviews adherence, progress, recovery, nutrition
  -> Planner Agent creates next week draft
  -> Replanning Agent checks constraints and risk
  -> Recommendation Agent ranks behavior changes
  -> Coach Agent explains the new plan
  -> User receives plan preview
```

---

## 10. AI Tool-Calling System

Agents should never directly query random database tables. They call approved tools.

Tool categories:

| Tool File | Example Functions |
|---|---|
| `workout_tools.py` | `get_current_plan`, `get_recent_sessions`, `update_workout_plan` |
| `nutrition_tools.py` | `get_daily_macros`, `log_meal_estimate`, `get_meal_history` |
| `analytics_tools.py` | `get_adherence_score`, `get_progress_trends`, `get_readiness_history` |
| `memory_tools.py` | `retrieve_user_memory`, `write_user_memory` |
| `scheduler_tools.py` | `get_user_schedule`, `move_workout_session` |
| `notification_tools.py` | `create_in_app_nudge`, `schedule_reminder` |

Tool safety rules:

- Tools must validate `user_id`.
- Tools must return structured JSON.
- Write tools require explicit orchestrator permission.
- Risky changes should create proposed actions before committing.
- All tool calls are logged for debugging.

---

## 11. Request Lifecycle Architecture

Standard API request:

```text
Frontend page/component
  -> service function using Axios
  -> FastAPI route
  -> dependency injection validates user
  -> module service runs business logic
  -> repository reads/writes PostgreSQL
  -> service optionally emits event
  -> response returned
  -> frontend updates UI
```

AI request:

```text
Frontend CoachChat
  -> POST /ai-coach/messages
  -> ai_coach/routes.py
  -> ai_coach/service.py
  -> coaching_orchestrator.py
  -> Memory Agent retrieves context
  -> tool calls fetch structured facts
  -> Coach Agent generates response
  -> message saved
  -> response streamed or returned
```

Event-triggered AI request:

```text
Module service emits event
  -> Redis queue
  -> worker consumes event
  -> event handler starts AI pipeline
  -> database and memory updated
  -> websocket notification sent
```

---

## 12. Database Interaction Flow

PostgreSQL is the source of truth.

Core tables:

```text
users
user_profiles
user_goals
workout_plans
workout_sessions
exercises
exercise_sets
meals
meal_items
nutrition_targets
sleep_logs
recovery_metrics
adherence_scores
recommendations
plan_changes
coach_conversations
coach_messages
events
memory_records
uploads
notifications
```

Qdrant collections:

```text
user_memory
coach_conversations
behavior_patterns
fitness_knowledge
nutrition_knowledge
```

Redis usage:

```text
cache:user:{user_id}:dashboard
cache:user:{user_id}:readiness
events:fitness
ws:user:{user_id}:connections
jobs:ai
rate_limit:{user_id}
```

Database access rules:

- Routes never query DB directly.
- Services use repositories.
- AI tools call services or repositories through approved interfaces.
- Repositories do not contain AI logic.
- Memory writes include source event and audit metadata.

---

## 13. Realtime Communication Flow

Use WebSockets for live dashboard updates, AI job status, chat streaming, and recommendations.

Suggested channels:

```text
user:{user_id}:dashboard
user:{user_id}:coach
user:{user_id}:recommendations
user:{user_id}:jobs
```

Realtime flow:

```text
AI pipeline updates recommendation
  -> recommendation saved in PostgreSQL
  -> websocket_manager publishes message
  -> frontend useWebSocket receives update
  -> dashboard card animates with Framer Motion
```

Message shape:

```json
{
  "type": "recommendation.updated",
  "channel": "dashboard",
  "payload": {
    "title": "Shift today's workout",
    "reason": "Low sleep and high fatigue detected",
    "priority": "high"
  }
}
```

---

## 14. Suggested API Structure

Base prefix:

```text
/api/v1
```

Endpoints:

```text
POST   /auth/register
POST   /auth/login
POST   /auth/refresh
GET    /users/me
PATCH  /users/me

GET    /dashboard/today

GET    /workouts/plans
POST   /workouts/plans
GET    /workouts/today
POST   /workouts/sessions/{session_id}/complete
POST   /workouts/sessions/{session_id}/miss

GET    /nutrition/today
POST   /nutrition/meals
POST   /nutrition/meals/analyze-image
GET    /nutrition/targets

GET    /sleep/logs
POST   /sleep/logs

GET    /recovery/readiness
POST   /recovery/check-in

GET    /analytics/weekly
GET    /analytics/adherence
GET    /analytics/progress

GET    /recommendations
POST   /recommendations/{recommendation_id}/accept
POST   /recommendations/{recommendation_id}/dismiss

POST   /replanning/run
GET    /replanning/history

POST   /ai-coach/messages
GET    /ai-coach/conversations
GET    /ai-coach/conversations/{conversation_id}

POST   /uploads/images
```

WebSocket endpoints:

```text
WS /ws/dashboard
WS /ws/coach
WS /ws/jobs
```

---

## 15. Deployment Architecture

Local development:

```text
Docker Compose:
  frontend
  backend
  worker
  postgres
  redis
  qdrant
```

Production:

```text
Kubernetes:
  frontend deployment
  backend API deployment
  AI worker deployment
  Redis deployment or managed Redis
  Qdrant deployment or managed Qdrant
  managed PostgreSQL
  S3 for uploads
  ingress controller
  cert manager
  monitoring stack
```

Recommended production split:

| Service | Purpose |
|---|---|
| `frontend` | Next.js app. |
| `backend-api` | FastAPI HTTP and WebSocket server. |
| `ai-worker` | Event consumers and AI pipelines. |
| `scheduler-worker` | Scheduled reports, nightly checks, weekly plans. |
| `postgres` | Managed database preferred. |
| `redis` | Cache, queues, websocket coordination. |
| `qdrant` | Vector memory. |

---

## 16. Docker Structure

`docker-compose.yml` should run:

```text
frontend:
  build: ./frontend
  ports: 3000:3000

backend:
  build: ./backend
  ports: 8000:8000
  depends_on: postgres, redis, qdrant

worker:
  build: ./backend
  command: python -m app.tasks.worker
  depends_on: backend, redis, postgres, qdrant

postgres:
  image: postgres:16

redis:
  image: redis:7

qdrant:
  image: qdrant/qdrant
```

Docker best practices:

- Separate frontend and backend images.
- Use `.env.example` only for documentation.
- Run migrations before API startup in deployment pipeline.
- Keep AI workers horizontally scalable.
- Do not bake secrets into images.

---

## 17. Kubernetes-Ready Organization

Kubernetes files should stay environment-neutral in `infra/k8s/base`.

Use overlays:

```text
dev       smaller resources, debug logs
staging   production-like, test secrets
production autoscaling, stricter limits
```

Kubernetes recommendations:

- API and worker scale independently.
- Use `HorizontalPodAutoscaler` for backend and worker.
- Use readiness and liveness probes.
- Store secrets in external secret manager for production.
- Use managed PostgreSQL for reliability.
- Keep Qdrant persistent volumes if self-hosted.

---

## 18. Best Practices

General:

- Start modular monolith, split services only when pain is real.
- Keep every feature easy to find.
- Use events for async intelligence.
- Keep prompts versioned and reviewable.
- Log agent inputs, selected tools, retrieved memory IDs, and output metadata.
- Treat AI output as proposed decisions unless the action is low risk.

Backend:

- Routes are thin.
- Services own business rules.
- Repositories own database queries.
- AI tools are the only way agents access product data.
- Use Pydantic schemas for every API boundary.
- Emit domain events after important state changes.

Frontend:

- One route equals one main screen.
- Keep feature components near their domain.
- Keep API calls in `services/`.
- Keep visual primitives reusable but simple.
- Avoid global state until truly needed.

AI:

- Ground answers in retrieved context.
- Store memory only when it is useful later.
- Use evaluation tests before prompt changes.
- Separate recommendation candidates from ranking.
- Keep rule-based safety checks around AI suggestions.

---

## 19. Naming Conventions

Frontend:

```text
Components: PascalCase.js
Hooks: useSomething.js
Services: somethingService.js
Utilities: camelCase.js
Routes: kebab-case folders where needed
```

Backend:

```text
Files: snake_case.py
Classes: PascalCase
Functions: snake_case
Schemas: CreateWorkoutPlanRequest, WorkoutPlanResponse
Models: WorkoutPlan, WorkoutSession
Events: domain.action, example workout.missed
```

AI:

```text
Agents: planner_agent.py
Pipelines: missed_workout_pipeline.py
Prompts: planner.md
Tools: workout_tools.py
Evaluations: test_planner_agent.py
```

---

## 20. Scaling Strategy

Phase 1:

- Monorepo.
- One FastAPI API process.
- One worker process.
- PostgreSQL, Redis, Qdrant through Docker Compose.
- Basic AI pipelines.

Phase 2:

- Separate API and worker deployments.
- Add scheduled worker.
- Add Redis queue groups.
- Add observability.
- Add prompt and retrieval evaluation.

Phase 3:

- Horizontally scale API.
- Horizontally scale AI workers by event type.
- Add model gateway for multiple AI providers.
- Add feature store for analytics models.
- Move heavy meal analysis into dedicated worker queue.

Phase 4:

- Split AI service only if needed.
- Add personalization model training.
- Add experiment framework for recommendations.
- Add advanced safety and medical-disclaimer review workflows.

---

## 21. Security Recommendations

- Use JWT access tokens plus refresh tokens.
- Hash passwords with Argon2 or bcrypt.
- Validate file uploads by MIME type and size.
- Store uploads in S3 with private buckets and signed URLs.
- Use row-level user ownership checks in every repository query.
- Rate-limit auth, chat, upload, and AI endpoints.
- Log security events.
- Do not expose chain-of-thought to users.
- Store only safe AI reasoning summaries for debugging.
- Encrypt sensitive environment variables.
- Add nutrition and fitness safety disclaimers.
- Require user confirmation before high-impact plan changes if risk is elevated.
- Never present AI as a doctor, dietitian, or emergency medical service.

---

## 22. Where To Change What

| Change Needed | File or Folder |
|---|---|
| Add a new dashboard card | `frontend/features/dashboard/components/` |
| Change API URL handling | `frontend/services/apiClient.js` |
| Add workout endpoint | `backend/app/modules/workouts/routes.py` |
| Add workout business rule | `backend/app/modules/workouts/service.py` |
| Add database query | `backend/app/modules/workouts/repository.py` |
| Add AI workout adjustment | `backend/app/ai/agents/replanning_agent.py` |
| Change coach personality | `backend/app/ai/prompts/coach.md` |
| Improve memory retrieval | `backend/app/ai/memory/retriever.py` |
| Change recommendation ranking | `backend/app/ai/recommendations/ranker.py` |
| Add event reaction | `backend/app/events/handlers/` |
| Add websocket update | `backend/app/realtime/channels.py` |
| Add Kubernetes config | `infra/k8s/base/` |
| Add AI test | `backend/app/ai/evaluation/` |

---

## 23. Beginner Explanation

Think of the system as five layers:

```text
Frontend:
  What the user sees.

Backend modules:
  Normal app features like workouts, meals, sleep, and analytics.

AI layer:
  Agents, memory, prompts, tools, and recommendation logic.

Event layer:
  The nervous system that notices behavior and triggers AI actions.

Data layer:
  PostgreSQL for facts, Qdrant for memory search, Redis for realtime and queues.
```

Simple mental model:

```text
User does something
  -> Backend saves it
  -> Event is created
  -> AI decides if anything should change
  -> Database stores the result
  -> Frontend updates live
```

---

## 24. Interview Explanation

Short interview version:

```text
I designed an adaptive AI fitness operating system using a modular Next.js and FastAPI monorepo. The backend is feature-first, so workouts, nutrition, recovery, analytics, recommendations, and coaching each own their routes, schemas, models, repositories, services, and tests.

The AI layer is separated into agents, prompts, tools, memory, orchestration, pipelines, and evaluation. Events like missed workouts, poor sleep, and overeating are published to Redis, consumed by workers, and routed into AI pipelines. PostgreSQL stores source-of-truth user data, Qdrant stores semantic long-term memory, and Redis powers queues, caching, and WebSockets.

The system is proactive because it reacts to behavior. For example, a missed workout triggers recovery analysis, plan redistribution, nutrition adjustment, recommendation updates, memory writes, and a coach explanation pushed to the dashboard in realtime.
```

---

## 25. Developer Onboarding

Day 1:

```text
1. Read README.md.
2. Run docker-compose up.
3. Open frontend on localhost:3000.
4. Open FastAPI docs on localhost:8000/docs.
5. Create a user.
6. Complete or miss a workout.
7. Watch event logs and realtime dashboard update.
```

First files to understand:

```text
frontend/app/dashboard/page.js
frontend/services/apiClient.js
backend/app/main.py
backend/app/modules/workouts/routes.py
backend/app/modules/workouts/service.py
backend/app/events/event_bus.py
backend/app/ai/orchestrators/event_orchestrator.py
backend/app/ai/pipelines/missed_workout_pipeline.py
```

---

## 26. Recommended Coding Patterns

Backend service pattern:

```text
route validates request
service performs business logic
repository reads/writes database
service emits event
route returns schema response
```

AI pipeline pattern:

```text
load event
load structured user state
retrieve memory
run required agents
validate proposed actions
persist changes
publish realtime update
write memory
```

Frontend screen pattern:

```text
page.js
  loads feature hook
  renders feature components
  uses shared visual components
  calls services through hooks
```

---

## 27. Suggested AI Workflow Structure

For every AI feature:

```text
1. Define trigger:
   API request, event, scheduled job, or chat intent.

2. Define required context:
   Structured PostgreSQL data plus semantic Qdrant memory.

3. Define tools:
   Explicit functions the agent can call.

4. Define prompt:
   Role, rules, output schema, safety boundaries.

5. Define pipeline:
   Ordered steps and fallback behavior.

6. Define persistence:
   What is saved to PostgreSQL and Qdrant.

7. Define evaluation:
   Test cases, expected behavior, failure cases.
```

---

## 28. Testing Structure

Frontend tests:

```text
component tests for cards, chat, forms
route smoke tests
service tests with mocked Axios
visual regression for dashboard states
```

Backend tests:

```text
unit tests for services
repository tests against test database
API integration tests
event handler tests
WebSocket tests
```

AI tests:

```text
prompt regression tests
retrieval relevance tests
agent output schema tests
tool permission tests
recommendation ranking tests
pipeline integration tests
safety tests
```

Example AI evaluation cases:

```text
missed workout after poor sleep should reduce intensity
missed workout after normal recovery should reschedule volume
meal over target should suggest correction without shame language
coach should not invent workout history
recommendation should cite relevant user behavior
```

---

## 29. Monitoring And Logging

Application logs:

- Request ID.
- User ID hash.
- Endpoint.
- Latency.
- Error type.
- Event ID.

AI logs:

- Agent name.
- Prompt version.
- Retrieved memory IDs.
- Tool calls.
- Output schema validation result.
- Confidence score.
- Safety flags.
- Latency and token usage.

Metrics:

```text
api_request_latency
api_error_rate
ai_pipeline_latency
ai_tool_call_count
ai_retrieval_empty_rate
recommendation_acceptance_rate
missed_workout_recovery_rate
websocket_connected_clients
event_queue_depth
```

Dashboards:

- API health.
- AI pipeline health.
- Retrieval quality.
- Queue depth.
- Recommendation acceptance.
- User adherence trends.

Alerting:

- High API error rate.
- AI worker failures.
- Redis queue backlog.
- Qdrant unavailable.
- PostgreSQL connection exhaustion.
- Abnormally high AI cost.

---

## 30. Production Practicality Notes

Avoid overengineering early:

- Do not split agents into separate services on day one.
- Do not add Redux.
- Do not build a custom workflow engine at the start.
- Do not train models before enough data exists.
- Do not store every chat message as semantic memory.

Build first:

```text
auth
user profile and goals
workout plans and sessions
nutrition logging
sleep and recovery check-ins
dashboard
AI coach chat
missed workout pipeline
recommendation cards
basic memory retrieval
weekly analytics report
```

Then add:

```text
meal image analysis
advanced adherence prediction
habit optimization
calendar integration
wearable integrations
experimentation framework
model fine-tuning or custom predictors
```

---

## 31. Final System Summary

This architecture creates a product that feels like a funded AI startup while staying manageable for a beginner developer.

The frontend is premium but simple:

```text
routes + components + features + services + hooks
```

The backend is scalable but understandable:

```text
feature modules + services + repositories + events
```

The AI system is organized and debuggable:

```text
agents + prompts + tools + memory + pipelines + evaluation
```

The intelligence loop is the heart of the product:

```text
Observe behavior
  -> store facts
  -> create events
  -> retrieve memory
  -> run agents
  -> adapt plans
  -> explain changes
  -> update dashboard
  -> learn for next time
```
