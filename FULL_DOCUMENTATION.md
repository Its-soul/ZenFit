# AI Fitness OS Developer Documentation

## 1. Project Overview

AI Fitness OS is a modular monorepo for an adaptive, AI-first fitness operating system. It combines a Next.js frontend, FastAPI backend, PostgreSQL relational storage, Redis event/realtime infrastructure, and Qdrant vector memory.

The application flow is:

```text
Next.js UI
  -> Axios service layer
  -> FastAPI feature routes
  -> feature services/repositories
  -> PostgreSQL
  -> domain events
  -> Redis queue
  -> AI worker
  -> Qdrant memory + recommendations + replanning
  -> Redis realtime channel
  -> WebSocket dashboard updates
```

### Main Frameworks And Libraries

Frontend:

- `Next.js 16.2.6`, App Router: `frontend/app`
- `React 19.2.6`
- `Tailwind CSS`
- `Framer Motion`
- `Axios`
- `lucide-react`

Backend:

- `FastAPI`
- `SQLAlchemy`
- `Alembic`
- `psycopg`
- `python-jose` for JWT
- `passlib[bcrypt]` for password hashing
- `redis`
- `qdrant-client`
- `pydantic-settings`

Infrastructure:

- Docker Compose: `docker-compose.yml`
- PostgreSQL: `postgres` service
- Redis: `redis` service
- Qdrant: `qdrant` service
- Backend API: `backend` service
- AI event worker: `worker` service
- Scheduled AI jobs: `scheduler` service
- Frontend: `frontend` service

### Main Entry Points

| Area | Entry Point | Purpose |
|---|---|---|
| Frontend app | `frontend/app/layout.js` | Root Next.js layout. |
| Frontend redirect | `frontend/app/page.js` | Redirects `/` to `/dashboard`. |
| Frontend API client | `frontend/services/apiClient.js` | Axios instance and auth header injection. |
| Backend app | `backend/app/main.py` | Creates FastAPI app, registers routers, starts realtime listener. |
| Backend DB | `backend/app/db/session.py` | SQLAlchemy engine and session factory. |
| Backend migrations | `backend/alembic/env.py` | Alembic migration runtime. |
| Event worker | `backend/app/tasks/worker.py` | Consumes Redis event queue. |
| Scheduler | `backend/app/tasks/scheduler.py` | Runs scheduled AI jobs periodically. |
| Demo seed | `scripts/seed_demo_data.py` | Generates demo users and long-term historical data. |
| AI eval | `scripts/evaluate_ai.py` | Runs AI regression/evaluation checks. |

### Environment Setup

Local development is Docker-first:

```bash
docker compose up --build
```

Important local URLs:

- Frontend: `http://localhost:3000`
- Backend docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/v1/health`
- Qdrant dashboard: `http://localhost:6333/dashboard`

Local scripts:

```bash
python scripts/evaluate_ai.py
python scripts/seed_demo_data.py
python scripts/seed_demo_data.py --days 365
```

## 2. Authentication System

Full details are in `AUTH_FLOW.md`.

Summary:

| Topic | Implementation |
|---|---|
| Auth provider | Custom email/password auth. No OAuth/Auth.js/Firebase/Supabase. |
| JWT/session handling | Stateless JWT bearer token, created in `backend/app/core/security.py`. |
| Backend middleware | No auth middleware class; FastAPI dependency `get_current_user` protects routes. |
| Frontend protection | Client-side `useAuth({ requireAuth: true })`; no `middleware.js`. |
| Login flow | `frontend/app/auth/login/page.js` -> `authService.login` -> `POST /auth/login` -> `localStorage`. |
| Logout flow | `AppShell` logout -> `useAuth.logout` -> `clearAuthSession` -> `/auth/login`. |
| Token storage | `localStorage.fitness_os_token`. |
| User cache | `localStorage.fitness_os_user`. |
| Session storage | None. |
| Cookies | None. |
| Redux/Zustand/context | None. |
| Database auth table | PostgreSQL `users`, model `backend/app/modules/auth/models.py`. |

Exact auth storage code:

```javascript
// frontend/lib/authStorage.js
const TOKEN_KEY = "fitness_os_token";
const USER_KEY = "fitness_os_user";
```

Backend route protection:

```python
# backend/app/dependencies.py
bearer_scheme = HTTPBearer(auto_error=False)
```

Security note: localStorage JWT storage is acceptable for local development but should be replaced with secure HTTP-only cookie auth or another hardened strategy before production.

## 3. Demo Data Documentation

Full details are in `DEMO_DATA_MAP.md`.

Demo/sample/test data found:

| Dataset | File | Static/Dynamic | Used By |
|---|---|---|---|
| Demo personas | `backend/app/demo/profiles.py` | Static definitions | Demo seeder/simulator. |
| Demo behavior simulation | `backend/app/demo/simulation.py` | Dynamic deterministic generation | Demo seeder. |
| Demo seed writer | `backend/app/demo/seeder.py` | Dynamic writes | `scripts/seed_demo_data.py`. |
| Seed CLI | `scripts/seed_demo_data.py` | Dynamic execution | Developer command. |
| Prompt regression cases | `backend/app/ai/evaluation/datasets/prompt_regression_cases.json` | Static JSON | AI eval runner. |
| Recommendation cases | `backend/app/ai/evaluation/datasets/recommendation_cases.json` | Static JSON | AI eval runner. |
| Frontend starter messages/forms | `frontend/app/*/page.js` | Static UI defaults | Individual pages. |
| Navigation array | `frontend/components/layout/AppShell.js` | Static UI metadata | Sidebar. |

No fake API response files, mock API handlers, MSW setup, or hardcoded frontend analytics JSON were found.

## 4. Demo Data Locations

See `DEMO_DATA_MAP.md` for the full table:

```text
Type | File Path | Used By | Notes
```

The important runtime demo-data path is:

```text
scripts/seed_demo_data.py
  -> backend/app/demo/seeder.py
  -> backend/app/demo/simulation.py
  -> PostgreSQL + Qdrant
```

## 5. Database + Storage

Full storage details are in `STORAGE_LOCATIONS.md`.

Summary:

| Storage | Purpose | Key Files |
|---|---|---|
| PostgreSQL | Source-of-truth relational data | `backend/app/db/session.py`, `backend/app/modules/*/models.py` |
| Alembic | Schema migrations | `backend/alembic/versions/*.py` |
| Qdrant | Semantic memory vectors | `backend/app/core/qdrant_client.py`, `backend/app/ai/memory/vector_store.py` |
| Redis | Queues and pub/sub | `backend/app/events/event_bus.py`, `backend/app/core/redis_client.py` |
| Browser localStorage | Auth token/user cache | `frontend/lib/authStorage.js` |
| Docker volumes | Local persistence | `docker-compose.yml` |

There is no Firebase, Supabase, MongoDB, or cloud storage implementation in the active codebase.

---

## Backend Architecture Details

The backend uses a feature-first modular structure:

```text
backend/app/modules/{feature}/
  routes.py       FastAPI endpoints
  schemas.py      Pydantic request/response contracts
  models.py       SQLAlchemy models
  repository.py   Database queries
  service.py      Business logic
```

Feature modules:

| Module | Files | Responsibility |
|---|---|---|
| Auth | `backend/app/modules/auth/*` | Register, login, JWT issuing, current user. |
| Users | `backend/app/modules/users/*` | Profile and onboarding. |
| Dashboard | `backend/app/modules/dashboard/*` | Aggregated dashboard data. |
| Workouts | `backend/app/modules/workouts/*` | Workout sessions, completion, missed events. |
| Nutrition | `backend/app/modules/nutrition/*` | Meal logs and daily totals. |
| Sleep | `backend/app/modules/sleep/*` | Sleep logs and poor sleep events. |
| Recovery | `backend/app/modules/recovery/*` | Recovery check-ins and readiness score. |
| Recommendations | `backend/app/modules/recommendations/*` | Recommendation listing and feedback. |
| Analytics | `backend/app/modules/analytics/*` | Predictions, history, weekly report APIs. |
| Memory | `backend/app/modules/memory/*` | Qdrant memory search API. |
| AI Coach | `backend/app/modules/ai_coach/*` | Coach chat endpoint. |

## AI Architecture

AI code is isolated under `backend/app/ai`.

| Folder | Purpose |
|---|---|
| `agents` | Agent classes: coach, memory, recovery, replanning. |
| `orchestrators` | Multi-step coordination, currently coaching orchestration. |
| `pipelines` | Adaptive replanning pipeline. |
| `memory` | Chunking, embeddings, Qdrant vector store, retrieval, reranking, decay, compression. |
| `recommendations` | Recommendation candidates and ranking. |
| `analytics` | Behavior patterns, prediction, personalization, trend detection. |
| `evaluation` | Prompt, retrieval, recommendation, schema, hallucination, tool-call checks. |
| `tools` | Approved agent tools. |
| `prompts` | Prompt text, currently `coach.md`. |

Important AI files:

- `backend/app/ai/agents/coach_agent.py`
- `backend/app/ai/agents/recovery_agent.py`
- `backend/app/ai/agents/replanning_agent.py`
- `backend/app/ai/orchestrators/coaching_orchestrator.py`
- `backend/app/ai/pipelines/adaptive_replanning_pipeline.py`
- `backend/app/ai/memory/vector_store.py`
- `backend/app/ai/memory/embeddings.py`
- `backend/app/ai/memory/retriever.py`
- `backend/app/ai/recommendations/candidate_generator.py`
- `backend/app/ai/recommendations/ranker.py`
- `backend/app/ai/analytics/predictors.py`
- `backend/app/ai/observability.py`

## Event-Driven System

Domain events are stored in PostgreSQL and queued in Redis.

Important files:

- Event model: `backend/app/events/models.py`
- Event types: `backend/app/events/event_types.py`
- Producer: `backend/app/events/producer.py`
- Redis bus: `backend/app/events/event_bus.py`
- Consumer: `backend/app/events/consumer.py`
- AI handler: `backend/app/events/handlers/ai_event_handler.py`
- Worker entry: `backend/app/tasks/worker.py`

Redis keys/channels:

| Name | Type | Purpose |
|---|---|---|
| `fitness.events.queue` | Redis list | Main background event queue. |
| `fitness.events.retry` | Redis list | Failed events after retry limit. |
| `fitness.events` | Pub/Sub | Event notification channel. |
| `fitness.realtime` | Pub/Sub | Worker-to-API realtime messages. |

Example flow:

```text
POST /workouts/sessions/{id}/miss
  -> WorkoutService.miss_session
  -> EventProducer.emit(workout.missed)
  -> domain_events row
  -> Redis queue message
  -> worker consumes message
  -> AIEventHandler writes Qdrant memory
  -> AdaptiveReplanningPipeline creates replacement session
  -> recommendations generated
  -> realtime update published
  -> WebSocket dashboard updates
```

## Frontend Architecture

Frontend structure:

```text
frontend/app          Route pages
frontend/components   Shared UI/layout components
frontend/services     API wrappers
frontend/hooks        Reusable client hooks
frontend/lib          Small utilities and auth storage
```

Important route pages:

| Route | File |
|---|---|
| `/` | `frontend/app/page.js` |
| `/auth/login` | `frontend/app/auth/login/page.js` |
| `/auth/register` | `frontend/app/auth/register/page.js` |
| `/onboarding` | `frontend/app/onboarding/page.js` |
| `/dashboard` | `frontend/app/dashboard/page.js` |
| `/workouts` | `frontend/app/workouts/page.js` |
| `/nutrition` | `frontend/app/nutrition/page.js` |
| `/sleep` | `frontend/app/sleep/page.js` |
| `/recovery` | `frontend/app/recovery/page.js` |
| `/coach` | `frontend/app/coach/page.js` |
| `/analytics` | `frontend/app/analytics/page.js` |
| `/settings` | `frontend/app/settings/page.js` |

## 6. API Layer

Backend base prefix is configured by `API_V1_PREFIX`, default `/api/v1`.

### REST Routes

| Method | Path | Backend File | Purpose |
|---|---|---|---|
| GET | `/api/v1/health` | `backend/app/main.py` | Service, Redis, Qdrant health. |
| POST | `/api/v1/auth/register` | `backend/app/modules/auth/routes.py` | Register user. |
| POST | `/api/v1/auth/login` | `backend/app/modules/auth/routes.py` | Login user. |
| GET | `/api/v1/auth/me` | `backend/app/modules/auth/routes.py` | Current user. |
| GET | `/api/v1/users/me/profile` | `backend/app/modules/users/routes.py` | Current profile. |
| POST | `/api/v1/users/me/onboarding` | `backend/app/modules/users/routes.py` | Complete onboarding. |
| GET | `/api/v1/dashboard/today` | `backend/app/modules/dashboard/routes.py` | Dashboard aggregate. |
| GET | `/api/v1/workouts/sessions` | `backend/app/modules/workouts/routes.py` | List workouts. |
| GET | `/api/v1/workouts/today` | `backend/app/modules/workouts/routes.py` | Today workout, auto-created if absent. |
| POST | `/api/v1/workouts/sessions` | `backend/app/modules/workouts/routes.py` | Create workout. |
| POST | `/api/v1/workouts/sessions/{session_id}/complete` | `backend/app/modules/workouts/routes.py` | Mark complete. |
| POST | `/api/v1/workouts/sessions/{session_id}/miss` | `backend/app/modules/workouts/routes.py` | Mark missed. |
| GET | `/api/v1/nutrition/today` | `backend/app/modules/nutrition/routes.py` | Daily nutrition totals. |
| POST | `/api/v1/nutrition/meals` | `backend/app/modules/nutrition/routes.py` | Create meal. |
| GET | `/api/v1/sleep/logs` | `backend/app/modules/sleep/routes.py` | List recent sleep logs. |
| POST | `/api/v1/sleep/logs` | `backend/app/modules/sleep/routes.py` | Create/update sleep log. |
| GET | `/api/v1/recovery/readiness` | `backend/app/modules/recovery/routes.py` | Latest recovery check-in. |
| POST | `/api/v1/recovery/check-ins` | `backend/app/modules/recovery/routes.py` | Create/update recovery check-in. |
| GET | `/api/v1/recommendations` | `backend/app/modules/recommendations/routes.py` | Active recommendations. |
| POST | `/api/v1/recommendations/{recommendation_id}/feedback` | `backend/app/modules/recommendations/routes.py` | Accept/dismiss feedback. |
| POST | `/api/v1/ai-coach/messages` | `backend/app/modules/ai_coach/routes.py` | Coach message. |
| POST | `/api/v1/memory/search` | `backend/app/modules/memory/routes.py` | Semantic memory search. |
| GET | `/api/v1/analytics/predictive` | `backend/app/modules/analytics/routes.py` | Predictions, patterns, personalization. |
| GET | `/api/v1/analytics/weekly-report/latest` | `backend/app/modules/analytics/routes.py` | Latest/generated weekly report. |
| GET | `/api/v1/analytics/history?days=90` | `backend/app/modules/analytics/routes.py` | Chart history from database. |

### WebSocket Routes

| Path | File | Auth |
|---|---|---|
| `/ws/dashboard?token={jwt}` | `backend/app/realtime/routes.py` | Query string JWT. |

### Frontend Service Files

| Service File | API Area |
|---|---|
| `frontend/services/authService.js` | Auth endpoints. |
| `frontend/services/userService.js` | Profile/onboarding. |
| `frontend/services/dashboardService.js` | Dashboard. |
| `frontend/services/workoutService.js` | Workouts. |
| `frontend/services/nutritionService.js` | Nutrition. |
| `frontend/services/sleepService.js` | Sleep. |
| `frontend/services/recoveryService.js` | Recovery. |
| `frontend/services/recommendationService.js` | Recommendation feedback. |
| `frontend/services/aiCoachService.js` | Coach chat. |
| `frontend/services/memoryService.js` | Memory search. |
| `frontend/services/analyticsService.js` | Predictive/history/report APIs. |

### Request Examples

Register:

```json
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "full_name": "User Example",
  "password": "password123"
}
```

Response:

```json
{
  "access_token": "jwt...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "User Example",
    "onboarding_complete": false
  }
}
```

Memory search:

```json
POST /api/v1/memory/search
{
  "query": "missed workout poor sleep adherence",
  "limit": 8
}
```

## Database And Storage Details

Primary database: PostgreSQL via SQLAlchemy.

Vector database: Qdrant collection `user_memory`.

Realtime/cache/queues: Redis.

Local file uploads are configured with `LOCAL_UPLOAD_DIR`, but no upload module is currently implemented in the active code.

### SQLAlchemy Models

| Table | Model File |
|---|---|
| `users` | `backend/app/modules/auth/models.py` |
| `user_profiles` | `backend/app/modules/users/models.py` |
| `workout_sessions` | `backend/app/modules/workouts/models.py` |
| `meals` | `backend/app/modules/nutrition/models.py` |
| `sleep_logs` | `backend/app/modules/sleep/models.py` |
| `recovery_checkins` | `backend/app/modules/recovery/models.py` |
| `recommendations` | `backend/app/modules/recommendations/models.py` |
| `recommendation_feedback` | `backend/app/modules/recommendations/feedback_models.py` |
| `domain_events` | `backend/app/events/models.py` |
| `ai_audit_logs` | `backend/app/ai/observability.py` |
| `ai_weekly_reports` | `backend/app/ai/reports.py` |

### Migrations

| Migration | Purpose |
|---|---|
| `backend/alembic/versions/0001_initial_auth_schema.py` | `users`, `user_profiles`. |
| `backend/alembic/versions/0002_core_fitness_schema.py` | Workouts, meals, sleep, recovery, recommendations, events. |
| `backend/alembic/versions/0003_predictive_intelligence_schema.py` | Recommendation explainability, feedback, AI audit logs, weekly reports. |

### Qdrant Storage

Configured in `backend/app/core/qdrant_client.py`.

Collection:

```text
user_memory
```

Vector size:

```text
384
```

Payload shape from `backend/app/ai/memory/vector_store.py`:

```json
{
  "user_id": "uuid",
  "text": "memory text",
  "category": "adherence",
  "source": "domain_event",
  "event_type": "workout.missed",
  "importance": 0.9,
  "created_at": "iso datetime"
}
```

## 7. Environment Variables

| Variable | Used In | Purpose | Default/Example |
|---|---|---|---|
| `APP_NAME` | `backend/app/config.py` | FastAPI title/name. | `AI Fitness OS` |
| `API_V1_PREFIX` | `backend/app/config.py`, `backend/app/main.py` | API route prefix. | `/api/v1` |
| `BACKEND_CORS_ORIGINS` | `backend/app/config.py`, `backend/app/main.py` | Allowed CORS origins. | `http://localhost:3000` |
| `DATABASE_URL` | `backend/app/config.py`, `backend/app/db/session.py`, `docker-compose.yml` | SQLAlchemy PostgreSQL URL. | `postgresql+psycopg://...` |
| `REDIS_URL` | `backend/app/config.py`, `backend/app/core/redis_client.py`, realtime listener | Redis URL. | `redis://localhost:6379/0` |
| `QDRANT_URL` | `backend/app/config.py`, `backend/app/core/qdrant_client.py` | Qdrant URL. | `http://localhost:6333` |
| `JWT_SECRET_KEY` | `backend/app/config.py`, `backend/app/core/security.py` | JWT signing secret. | Required unique secret. |
| `JWT_ALGORITHM` | `backend/app/config.py`, `backend/app/core/security.py` | JWT algorithm. | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `backend/app/config.py`, `backend/app/core/security.py` | Access JWT expiry. | `15` |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | `backend/app/config.py`, `backend/app/core/security.py` | Refresh JWT expiry. | `10080` |
| `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES` | `backend/app/config.py`, `backend/app/core/security.py` | Password reset JWT expiry. | `30` |
| `LOCAL_UPLOAD_DIR` | `backend/app/config.py` | Future local upload path. | `uploads` |
| `POSTGRES_DB` | `docker-compose.yml`, `.env.example` | Docker Postgres DB name. | `fitness_os` |
| `POSTGRES_USER` | `docker-compose.yml`, `.env.example` | Docker Postgres user. | `fitness_user` |
| `POSTGRES_PASSWORD` | `docker-compose.yml`, `.env.example` | Docker Postgres password. | Required local secret. |
| `NEXT_PUBLIC_API_URL` | `frontend/services/apiClient.js`, `docker-compose.yml` | Browser API base URL. | `http://localhost:8000/api/v1` |
| `NEXT_PUBLIC_WS_URL` | `frontend/hooks/useWebSocket.js`, `docker-compose.yml` | Browser WebSocket base URL. | `ws://localhost:8000/ws` |

Env files:

- Root: `.env.example`
- Backend: `backend/.env.example`

## 8. State Management

No Redux, Zustand, React Context auth provider, or global state library is used.

State patterns:

| State Type | Location | Mechanism |
|---|---|---|
| Access token | `frontend/lib/authStorage.js` | `localStorage` key `fitness_os_token`. |
| Refresh token | `frontend/lib/authStorage.js` | `localStorage` key `fitness_os_refresh_token`. |
| Stored user | `frontend/lib/authStorage.js` | `localStorage` key `fitness_os_user`. |
| Auth runtime state | `frontend/hooks/useAuth.js` | React `useState`, refreshed via `/auth/me`. |
| API cache | None | No React Query/SWR/cache layer. Data fetched per page. |
| Realtime state | `frontend/hooks/useWebSocket.js` | React `useState` for `status` and `lastMessage`. |
| Form state | Page components | React `useState`. |
| Backend worker queue | Redis | `fitness.events.queue`, `fitness.events.retry`. |

No `sessionStorage` usage was found.

No cookies are set by application code.

## 9. Security Review

Findings:

| Risk | Location | Notes |
|---|---|---|
| JWT stored in `localStorage` | `frontend/lib/authStorage.js` | Simple for local dev, vulnerable to XSS token theft. Prefer HTTP-only secure cookies in production. |
| Required JWT secret | `.env.example`, `backend/.env.example`, `backend/app/config.py` | The app rejects empty, placeholder, or weak JWT secrets. |
| Database password | `.env.example`, `docker-compose.yml` | Must be provided in untracked `.env`. |
| Demo user password | `backend/app/demo/profiles.py` | All demo accounts use `DemoPass123!`; public test credential. |
| WebSocket token in query string | `backend/app/realtime/routes.py`, `frontend/hooks/useWebSocket.js` | Query tokens can appear in logs. Prefer short-lived tokens or cookie auth for production. |
| Browser refresh token | `frontend/lib/authStorage.js` | Refresh tokens are revoked by `users.token_version`; prefer HTTP-only secure cookies in production. |
| CORS allows local frontend | `backend/app/main.py` | Safe for local, configure precise production origins. |
| No CSRF protection | Auth is bearer-token based | If moved to cookies, add CSRF strategy. |

Positive controls:

- Passwords hashed with bcrypt in `backend/app/core/security.py`.
- Backend route protection through `get_current_user` in `backend/app/dependencies.py`.
- Repository methods scope most user-owned reads by `user_id`.
- Demo seed hashes demo passwords before storage.

## 10. Final Deliverables

Generated deliverables:

| File | Purpose |
|---|---|
| `FULL_DOCUMENTATION.md` | Complete developer documentation report. |
| `DEMO_DATA_MAP.md` | Detailed inventory of demo/mock/sample/test/seed data and hardcoded development defaults. |
| `AUTH_FLOW.md` | Detailed authentication/session/token/protected-route documentation. |
| `STORAGE_LOCATIONS.md` | Detailed browser/PostgreSQL/Qdrant/Redis/local storage map. |

## Tests And Evaluation

No conventional frontend/backend unit test runner is configured yet.

AI evaluation exists:

- Runner: `scripts/evaluate_ai.py`
- Evaluation orchestrator: `backend/app/ai/evaluation/runner.py`
- Prompt dataset: `backend/app/ai/evaluation/datasets/prompt_regression_cases.json`
- Recommendation dataset: `backend/app/ai/evaluation/datasets/recommendation_cases.json`
- Retrieval tests: `backend/app/ai/evaluation/retrieval_tests.py`
- Hallucination checks: `backend/app/ai/evaluation/hallucination_tests.py`
- Schema/tool checks: `backend/app/ai/evaluation/schema_tests.py`

Run:

```bash
python scripts/evaluate_ai.py
```

## Generated/Dev Artifacts Found

The repository currently contains generated Python bytecode under `__pycache__` directories because compile checks were run. These are not source data and are ignored by `.gitignore`:

```text
backend/**/__pycache__/*
scripts/__pycache__/*
```

`frontend/package-lock.json` is dependency lock data, not app demo/mock data.
