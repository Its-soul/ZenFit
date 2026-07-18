# AI Fitness OS

Adaptive AI-first fitness operating system built as a clean modular monolith.

## Local Development

Requirements:

- Docker Desktop
- Node is optional if you run through Docker
- Python is optional if you run through Docker

Start everything:

```bash
# Configure the ignored root .env for your local machine.
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

## ZenFit AI

The new free/open-source, local-first intelligence code lives in `backend/app/zenfit_ai/`. It coexists with the previous `backend/app/ai/` implementation while integrations migrate. Configure the ignored root `.env`; no `.env.example` files are used.

```bash
docker compose build backend worker
docker compose run --rm backend python -m app.zenfit_ai.scripts.setup_models
docker compose up
docker compose run --rm backend python -m app.zenfit_ai.scripts.backfill_memory
docker compose run --rm backend pytest -q app/zenfit_ai/tests
docker compose run --rm backend python -m app.zenfit_ai.scripts.test_ai_stack
docker compose exec backend pytest -q -m integration
docker compose exec backend python -m app.zenfit_ai.scripts.evaluate_predictions
docker compose exec backend python -m app.zenfit_ai.scripts.benchmark_ai --runs 20
```

The authenticated local meal endpoint is `POST /api/v1/nutrition/meals/analyze-image-local`; confirm/correct its result with `POST /api/v1/nutrition/meals/confirm-analysis`. The old meal endpoint remains available during migration. BGE models cache on first setup. FoodSAM, FoodSeg103, and Indian-food weights are optional and report unavailable until separately installed with compatible licenses.

User interfaces are available at `/nutrition/meal-analysis` and `/workouts/form-check`. The form checker keeps camera frames in the browser and sends sampled landmarks. See `backend/app/zenfit_ai/docs/DEMO.md`, `MODELS.md`, and `DATASETS.md` for validated status and setup details.
