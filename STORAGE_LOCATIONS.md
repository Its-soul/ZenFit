# Storage Locations

## Overview

The project uses four storage layers:

1. Browser `localStorage` for local auth token/user cache.
2. PostgreSQL for relational source-of-truth data.
3. Qdrant for semantic vector memory.
4. Redis for queues, realtime pub/sub, and ephemeral event state.

No application cookies are used.

No `sessionStorage` is used.

No Firebase, Supabase, MongoDB, or external cloud storage is implemented.

## Browser Storage

Defined in:

```text
frontend/lib/authStorage.js
```

| Storage | Key | Data | Set By | Read By | Cleared By |
|---|---|---|---|---|---|
| `localStorage` | `fitness_os_token` | JWT access token | `saveAuthSession` | `getAccessToken`, Axios, WebSocket | `clearAuthSession` |
| `localStorage` | `fitness_os_user` | User JSON | `saveAuthSession` | `getStoredUser`, `useAuth` | `clearAuthSession` |

No `sessionStorage` calls were found.

No `document.cookie` or cookie-setting code was found.

## PostgreSQL

Configured in:

| File | Purpose |
|---|---|
| `backend/app/config.py` | `DATABASE_URL` setting. |
| `backend/app/db/session.py` | SQLAlchemy engine/session. |
| `backend/alembic/env.py` | Migration runtime. |
| `docker-compose.yml` | Local Postgres container. |

Docker service:

```text
postgres
```

Default local DB:

```text
fitness_os
```

### Tables

| Table | Model | Migration |
|---|---|---|
| `users` | `backend/app/modules/auth/models.py` | `0001_initial_auth_schema.py` |
| `user_profiles` | `backend/app/modules/users/models.py` | `0001_initial_auth_schema.py` |
| `workout_sessions` | `backend/app/modules/workouts/models.py` | `0002_core_fitness_schema.py` |
| `meals` | `backend/app/modules/nutrition/models.py` | `0002_core_fitness_schema.py` |
| `sleep_logs` | `backend/app/modules/sleep/models.py` | `0002_core_fitness_schema.py` |
| `recovery_checkins` | `backend/app/modules/recovery/models.py` | `0002_core_fitness_schema.py` |
| `recommendations` | `backend/app/modules/recommendations/models.py` | `0002_core_fitness_schema.py`, altered by `0003_predictive_intelligence_schema.py` |
| `recommendation_feedback` | `backend/app/modules/recommendations/feedback_models.py` | `0003_predictive_intelligence_schema.py` |
| `domain_events` | `backend/app/events/models.py` | `0002_core_fitness_schema.py` |
| `ai_audit_logs` | `backend/app/ai/observability.py` | `0003_predictive_intelligence_schema.py` |
| `ai_weekly_reports` | `backend/app/ai/reports.py` | `0003_predictive_intelligence_schema.py` |

### Relationship Summary

```text
users
  -> user_profiles
  -> workout_sessions
  -> meals
  -> sleep_logs
  -> recovery_checkins
  -> recommendations
  -> recommendation_feedback
  -> domain_events
  -> ai_audit_logs
  -> ai_weekly_reports
```

Most domain tables include `user_id` with `ON DELETE CASCADE`.

## Qdrant

Configured in:

```text
backend/app/core/qdrant_client.py
```

Used by:

| File | Purpose |
|---|---|
| `backend/app/ai/memory/vector_store.py` | Upsert/search Qdrant points. |
| `backend/app/ai/memory/memory_writer.py` | Writes memories with importance and duplicate suppression. |
| `backend/app/ai/memory/retriever.py` | Searches and reranks memories. |
| `backend/app/ai/memory/ingestion.py` | Event memory ingestion. |
| `backend/app/demo/seeder.py` | Seeds/deletes demo user memories. |

Collection:

```text
user_memory
```

Vector size:

```text
384
```

Embedding:

```text
backend/app/ai/memory/embeddings.py
```

This is deterministic local hashing-based embedding, not an external paid API.

Payload example:

```json
{
  "user_id": "uuid",
  "text": "User missed a workout...",
  "category": "adherence",
  "source": "domain_event",
  "event_type": "workout.missed",
  "source_event_id": "uuid",
  "importance": 0.9,
  "created_at": "2026-05-15T..."
}
```

## Redis

Configured in:

| File | Purpose |
|---|---|
| `backend/app/core/redis_client.py` | Redis client factory and health check. |
| `backend/app/events/event_bus.py` | Event queue/retry/realtime channels. |
| `backend/app/realtime/redis_listener.py` | Forwards worker realtime messages to WebSocket clients. |
| `docker-compose.yml` | Local Redis container. |

Redis names:

| Key/Channel | Type | Purpose |
|---|---|---|
| `fitness.events.queue` | List | Worker event queue. |
| `fitness.events.retry` | List | Events that exceeded retry limit. |
| `fitness.events` | Pub/Sub channel | Event notification channel. |
| `fitness.realtime` | Pub/Sub channel | Realtime payloads from worker to API. |

## Local Files

Potential upload path:

```text
uploads/
```

Configured by:

```text
LOCAL_UPLOAD_DIR
```

Current status:

- `uploads/` is ignored by `.gitignore`.
- No active upload API implementation exists in the current code.

## Docker Volumes

Defined in `docker-compose.yml`:

| Volume | Service | Purpose |
|---|---|---|
| `postgres_data` | `postgres` | PostgreSQL persistence. |
| `redis_data` | `redis` | Redis persistence. |
| `qdrant_data` | `qdrant` | Qdrant vector storage. |

Bind mounts:

| Host Path | Container Path | Service |
|---|---|---|
| `./backend` | `/app` | backend, worker, scheduler |
| `./uploads` | `/app/uploads` | backend, worker, scheduler |
| `./frontend` | `/app` | frontend |
| `/app/node_modules` | anonymous volume | frontend |
| `/app/.next` | anonymous volume | frontend |

## Seed And Evaluation Storage

| File | Writes To |
|---|---|
| `scripts/seed_demo_data.py` | PostgreSQL and Qdrant. |
| `backend/app/demo/seeder.py` | PostgreSQL and Qdrant. |
| `scripts/evaluate_ai.py` | No persistent writes. |
| `backend/app/ai/evaluation/*` | No persistent writes. |

## Generated Development Artifacts

Current generated artifacts found:

```text
backend/**/__pycache__/*
scripts/__pycache__/*
```

They are Python bytecode and are not persistent application storage.

They are covered by `.gitignore` through `__pycache__/` and `*.pyc`.

