# AI Fitness OS

Adaptive AI-first fitness operating system built as a clean modular monolith.

## Local Development

Requirements:

- Docker Desktop
- Node is optional if you run through Docker
- Python is optional if you run through Docker

Start everything:

```bash
cp .env.example .env
# Fill every placeholder before starting the stack.
docker compose up --build
```

Open:

- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs
- Backend health: http://localhost:8000/api/v1/health
- Qdrant: http://localhost:6333/dashboard

The first runnable slice includes:

- Next.js App Router frontend
- FastAPI backend
- PostgreSQL migrations
- Redis health integration
- Qdrant health integration
- JWT authentication
- User onboarding
- Protected dashboard
- Premium SaaS-style dashboard shell
- Redis-backed event queue
- Background AI worker
- Event-driven memory ingestion
- Qdrant semantic memory search
- Adaptive missed-workout replanning
- Event-driven recommendations
- Realtime AI dashboard updates
- Predictive analytics APIs
- Long-term personalization profiles
- AI audit logging
- Scheduled behavioral analysis and weekly reports
- AI evaluation datasets and regression runner

## Event-Driven AI Worker

The API emits domain events into Redis. The `worker` service consumes those events, writes long-term memory, ranks recommendations, runs adaptive replanning, and publishes realtime dashboard updates.

Useful local flow:

```text
Mark a workout missed
  -> workout.missed event stored in PostgreSQL
  -> Redis queue receives event
  -> worker writes memory to Qdrant
  -> worker creates a replacement session
  -> worker creates recommendations
  -> dashboard receives WebSocket update
```

Run scheduled AI jobs:

```bash
docker compose logs -f scheduler
```

Run local AI evaluations:

```bash
python scripts/evaluate_ai.py
```

Seed realistic demo history:

```bash
python scripts/seed_demo_data.py
python scripts/seed_demo_data.py --days 365
```

Demo account password:

```text
DemoPass123!
```
