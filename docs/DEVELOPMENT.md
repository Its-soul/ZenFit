# Development Guide

This document outlines the local setup, engineering rules, and file organization for ZenFit developers.

## 1. Local Development Setup

### Start the Stack
```bash
cp .env.example .env
# Fill POSTGRES_PASSWORD, DATABASE_URL, JWT_SECRET_KEY, and other external API keys.
docker compose up --build
```

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
# The frontend runs at http://localhost:3000
```
API endpoints are configured in `frontend/lib/runtimeConfig.js`.

### Backend (FastAPI & Workers)
The backend runs automatically via Docker Compose.
- **FastAPI API**: `http://localhost:8000`
- **Documentation**: `http://localhost:8000/docs`
- **Worker Logs**: `docker compose logs -f worker`
- **Realtime**: WebSocket channel for worker-to-API communication.

### Predictive Intelligence & AI Features
Ensure the local services (PostgreSQL, Redis, Qdrant) are running.
```bash
# Run AI health evaluations
python scripts/evaluate_ai.py
```

## 2. Developer File Map

| I want to... | Go to... |
|---|---|
| Edit login/register UI | `frontend/app/auth/` |
| Edit dashboard UI | `frontend/app/dashboard/` and `frontend/components/product/` |
| Edit workout UI | `frontend/app/workouts/` |
| Edit Meal Scan UI | `frontend/app/nutrition/meal-analysis/` |
| Edit frontend API clients | `frontend/services/` |
| Validate frontend deployment URLs | `frontend/lib/runtimeConfig.js` |
| Edit authentication backend | `backend/app/modules/auth/` |
| Edit workout backend | `backend/app/modules/workouts/` |
| Edit nutrition database/API logic | `backend/app/modules/nutrition/` |
| Edit Meal Scan AI | `backend/app/ai/meal_scan/` |
| Add an API router | Feature router under `backend/app/modules/`, then `backend/app/api/router.py` |
| Edit worker behavior | `backend/app/workers/` and `backend/app/events/` |
| Add a migration | `backend/alembic/versions/` |
| Train/evaluate a classifier | `backend/training/` |
| Add backend tests | `backend/tests/unit/` or `backend/tests/integration/` |
| Find local datasets/artifacts | `data/` (not deployment source) |

## 3. Engineering Rules

### System & APIs
- **No paid dependencies**: The system uses only open-source or free external APIs.
- **Data Privacy**: Every Qdrant query must filter by `user_id`. PostgreSQL facts remain the source of truth, while Qdrant is contextual memory.
- **Security**: Never commit secrets or create `.env.example` files containing real secrets.
- **Architecture**: Keep packages shallow, typed, and testable. Use `snake_case` for modules and `PascalCase` for classes.
- **Validation**: Validate public inputs, use structured schemas, and log stages/latency rather than raw sensitive text.

### AI & Data Features
- **No silent failures**: Status and fallback source must be visible. Optional models must fail gracefully and load lazily.
- **No medical diagnosis**: Avoid automatic dangerous/high-impact plan changes without user review.
- **Safety First**: Do not count pose repetitions when critical landmark visibility is below 0.6. Meal image bytes are request-temporary, and confirmation is owner-scoped and single-use.

## 4. End-to-End Demo

You can seed the database with realistic demo users (historical workouts, meals, sleep, recovery, events, recommendations) to test the UI.

```bash
# Seed demo accounts
python scripts/seed_demo_data.py
```
Demo users all use the password `DemoPass123!`. Example accounts:
- `ava.consistent@demo.fitness`
- `ben.weightloss@demo.fitness`

### Testing The Adaptive Flow
1. Register or login.
2. Open `/dashboard`.
3. Mark today's workout as missed.
4. Watch `docker compose logs -f worker`.
5. The worker should create memory, recommendations, and a replacement workout.
6. The dashboard should receive an `ai.event.processed` WebSocket message.
