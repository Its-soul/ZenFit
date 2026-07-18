# Developer File Map

| I want to… | Go to… |
|---|---|
| Edit login/register UI | `frontend/app/auth/` |
| Edit dashboard UI | `frontend/app/dashboard/` and `frontend/components/product/` |
| Edit workout UI | `frontend/app/workouts/` |
| Edit Meal Scan UI | `frontend/app/nutrition/meal-analysis/` |
| Edit frontend API clients | `frontend/services/` |
| Edit authentication backend | `backend/app/modules/auth/` |
| Edit workout backend | `backend/app/modules/workouts/` |
| Edit nutrition database/API logic | `backend/app/modules/nutrition/` |
| Edit Meal Scan AI | `backend/app/ai/meal_scan/` |
| Edit open-set decisions | `backend/app/ai/meal_scan/open_set.py` |
| Edit BGE memory | `backend/app/ai/memory/bge_embeddings.py`, `bge_reranker.py`, and `semantic_retriever.py` |
| Edit legacy event memory | `backend/app/ai/memory/ingestion.py`, `memory_writer.py`, and `retriever.py` |
| Edit prediction models | `backend/app/ai/predictions/` |
| Edit model artifact runtime | `backend/app/ai/artifacts/` |
| Add an API router | Feature router under `backend/app/modules/`, then `backend/app/api/router.py` |
| Edit worker behavior | `backend/app/workers/` and `backend/app/events/` |
| Add a migration | `backend/alembic/versions/` |
| Train/evaluate a classifier | `backend/training/` |
| Add backend tests | `backend/tests/unit/` or `backend/tests/integration/` |
| Deploy frontend | Use `frontend/` as Vercel Root Directory |
| Deploy backend | Use `backend/` as Railway/Render root |
| Read deployment instructions | `deployment/README.md` |
| Find local datasets/artifacts | `data/` (not deployment source) |
