# Architecture

ZenFit is a shallow monorepo with independent frontend and backend deployment boundaries.

```text
ZenFit/
├── frontend/                 Next.js website
│   ├── app/                  Pages and routes
│   ├── components/           Reusable UI
│   ├── hooks/                Browser hooks
│   ├── lib/                  Shared browser utilities
│   └── services/             HTTP/WebSocket clients
├── backend/                  FastAPI and worker deployment root
│   ├── app/
│   │   ├── api/              Router aggregation
│   │   ├── ai/               Single AI runtime package
│   │   │   ├── agents/       Coaching agents
│   │   │   ├── analytics/    Behavior and trend analysis
│   │   │   ├── artifacts/    Runtime artifact storage/checksums
│   │   │   ├── meal_scan/    Meal recognition and open-set decisions
│   │   │   ├── memory/       Legacy memory plus explicit BGE modules
│   │   │   ├── nutrition/    Nutrition parsing/targets
│   │   │   ├── pose/         Landmark analysis
│   │   │   ├── predictions/  Adherence/readiness/recommendation models
│   │   │   └── safety/       Transparent safety rules
│   │   ├── core/             Redis, Qdrant, and shared infrastructure
│   │   ├── db/               SQLAlchemy registration/session support
│   │   ├── events/           Domain event producer/consumer/handlers
│   │   ├── modules/          Business routes, services, schemas, models
│   │   ├── workers/          Worker and scheduler entrypoints
│   │   └── main.py           FastAPI assembly and lifecycle
│   ├── alembic/              Database migrations
│   ├── scripts/              Backend operational commands
│   ├── tests/                Unit, integration, evaluation, load, fixtures
│   └── training/             Offline dataset/model lifecycle
├── deployment/               Deployment map
├── docs/                     Project documentation
├── scripts/                  Repository-level developer commands
├── data/                     Ignored local/generated data and artifacts
└── docker-compose.yml        Local multi-service development
```

## Boundaries

The frontend depends only on configured backend URLs. Business/database code stays in `app/modules`; AI analysis stays in `app/ai`. `app/api/router.py` aggregates HTTP routers so `main.py` only owns application lifecycle. Workers reuse the backend package and differ only by command.

Training is not imported by FastAPI startup. Dataset acquisition, preparation, training, evaluation, promotion, and rollback are offline commands under `backend/training`. Runtime artifact verification stays under `backend/app/ai/artifacts`.

The canonical configuration loader is `backend/app/config.py`. `app/ai/config.py` only re-exports it for focused AI imports. PostgreSQL, Redis, Qdrant, and secrets come from environment configuration.

Nutrition image recognition is owned by `app/ai/meal_scan`; there is no separate cloud-vision provider path. Manual entry, text lookup, correction, and confirmation remain business-module behavior.

## Common edit locations

- Meal Scan: `backend/app/ai/meal_scan/`
- Workout business logic: `backend/app/modules/workouts/`
- Nutrition database/API logic: `backend/app/modules/nutrition/`
- Frontend nutrition page: `frontend/app/nutrition/`
- AI memory: `backend/app/ai/memory/`
- Training: `backend/training/`
- Migrations: `backend/alembic/`
- Deployment: `deployment/`, root `render.yaml`, and `backend/railway.toml`
