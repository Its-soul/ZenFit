# ZenFit Backend

This folder is the independently deployable FastAPI backend. `app/modules/` contains business features, `app/ai/` is the single AI runtime, `app/events/` handles domain events, `app/workers/` contains background entrypoints, `alembic/` owns migrations, `tests/` owns all backend tests, and `training/` contains offline ML workflows. The repository root `.env.example` is the single configuration template.

Required external services are PostgreSQL, Redis, and Qdrant. Model artifacts use persistent local or S3-compatible storage.

Run from this directory:

```powershell
python -m pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Worker and scheduler:

```powershell
python -m app.workers.main
python -m app.workers.scheduler
```

Lightweight tests:

```powershell
python -m pip install -r requirements-training.txt
python -m pytest -q tests -m "not integration and not model and not load and not external_api and not device_manual"
```

For Railway or Render, use `backend/` as the project root and `Dockerfile`. Initial deployments must set `AI_HEAVY_MODELS_ENABLED=false` and `AI_PREWARM_MODELS=false`, and keep the `INSTALL_AI=false` build default. Use `INSTALL_AI=true` only for a later, adequately provisioned AI stage after model promotion passes. No cloud meal-vision key is required.
