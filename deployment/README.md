# Deployment Map

## Frontend

Deploy folder: `frontend/`

Recommended target: Vercel. Set the Vercel Root Directory to `frontend`, use the detected Next.js build (`npm run build`), and configure `NEXT_PUBLIC_API_URL` plus `NEXT_PUBLIC_WS_URL`.

## Backend API

Deploy folder: `backend/`

Target: Railway or Render. Use `backend/Dockerfile` and start with:

```text
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set `AI_HEAVY_MODELS_ENABLED=false` and `AI_PREWARM_MODELS=false` for the initial deployment.

## Worker

Deploy the same `backend/` code and image as a separate Railway or Render worker. Start it with:

```text
python -m app.workers.main
```

The scheduler is another optional process: `python -m app.workers.scheduler`.

## Services and data

- Database: managed PostgreSQL.
- Cache and queue: managed Redis.
- Vector database: managed or external Qdrant.
- Model artifacts: persistent local disk or external S3-compatible artifact storage.
- Training code: `backend/training/`; do not execute it during web deployment.
- Training and Kaggle data: `data/`; do not deploy it.

`render.yaml` remains at repository root because Render Blueprints resolve repository build contexts there. Railway uses `backend/railway.toml` with the Railway project Root Directory set to `backend/`.
