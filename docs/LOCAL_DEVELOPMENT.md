# Local Development Workflow

## Start

```bash
cp .env.example .env
# Fill POSTGRES_PASSWORD, DATABASE_URL, JWT_SECRET_KEY, and USDA_FDC_API_KEY when live USDA lookup is needed.
docker compose up --build
```

## Stop

```bash
docker compose down
```

## Reset Local Data

```bash
docker compose down -v
docker compose up --build
```

## Backend

FastAPI runs on port `8000`.

Useful URLs:

- `GET /api/v1/health`
- Swagger docs at `/docs`

## Frontend

Next.js runs on port `3000`.

The frontend stores short-lived access and refresh tokens in `localStorage` for local development simplicity. In production, prefer secure HTTP-only cookies and keep `JWT_SECRET_KEY` unique per environment.

## AI Worker

Docker Compose runs a `worker` service:

```bash
docker compose logs -f worker
```

The worker consumes Redis queue messages from `fitness.events.queue`.

Important Redis keys/channels:

```text
fitness.events.queue      queued domain events
fitness.events.retry      events that exceeded retry count
fitness.events            event notification channel
fitness.realtime          worker-to-API realtime channel
```

## Predictive Intelligence

Available APIs:

```text
GET  /api/v1/analytics/predictive
GET  /api/v1/analytics/weekly-report/latest
POST /api/v1/recommendations/{recommendation_id}/feedback
```

The predictive layer uses:

```text
behavior_patterns.py      historical behavior analysis
predictors.py             adherence, recovery, fatigue, streak, workout probability
personalization.py        long-term user preference profile
trend_detector.py         plain-language trend detection
observability.py          AI audit logs
scheduled_jobs.py         nightly and weekly AI jobs
```

## AI Evaluation

Run:

```bash
python scripts/evaluate_ai.py
```

Current checks cover prompt regression, retrieval quality, hallucination guardrails, recommendation quality, agent output schema validation, and tool-call validation.

## Demo Data

Seed five realistic demo users with historical workouts, meals, sleep, recovery, events, recommendations, feedback, Qdrant memories, and weekly reports:

```bash
python scripts/seed_demo_data.py
```

Generate a longer one-year history:

```bash
python scripts/seed_demo_data.py --days 365
```

The script resets only the known demo accounts by default, then recreates them with deterministic data. Use `--keep-existing` to skip accounts that already exist.

Demo users all use:

```text
DemoPass123!
```

Example accounts:

```text
ava.consistent@demo.fitness
ben.weightloss@demo.fitness
maya.inconsistent@demo.fitness
leo.fatigue@demo.fitness
nina.musclegain@demo.fitness
```

## Testing The Adaptive Flow

1. Register and complete onboarding.
2. Open `/dashboard`.
3. Mark today's workout as missed.
4. Watch `docker compose logs -f worker`.
5. The worker should create memory, recommendations, and a replacement workout.
6. The dashboard should receive an `ai.event.processed` WebSocket message.
