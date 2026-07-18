# ZenFit

ZenFit is a deployable monorepo with clear frontend, backend, training, data, and deployment boundaries.

```text
frontend/    Next.js website; deploy to Vercel
backend/     FastAPI API, canonical AI runtime, workers, migrations, and offline training
deployment/  Platform map and deployment instructions
docs/        Architecture, AI, product, data, storage, and release documentation
scripts/     Repository-level developer utilities
data/        Local/generated datasets, uploads, and model artifacts; not deployed
```

## Quick start

Copy `.env.example` to the ignored `.env`, replace placeholder secrets, then run:

```powershell
docker compose up --build
```

Frontend-only development:

```powershell
cd frontend
npm install
npm run dev
```

Backend commands run from `backend/`:

```powershell
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
python -m app.workers.main
```

## Deployment

- Vercel Root Directory: `frontend/`
- Railway or Render backend root: `backend/`
- API command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Worker command: `python -m app.workers.main`

See [deployment/README.md](deployment/README.md) for PostgreSQL, Redis, Qdrant, artifact storage, Render, and Railway details.

## AI and training

The only AI runtime package is `backend/app/ai/`. Offline acquisition, preparation, training, evaluation, promotion, and rollback live in `backend/training/` and are never invoked by web startup.

Initial deployments must use:

```env
AI_HEAVY_MODELS_ENABLED=false
AI_PREWARM_MODELS=false
```

Runtime dependencies are in `backend/requirements.txt`; optional heavy AI dependencies are in `backend/requirements-ai.txt`; training dependencies are in `backend/requirements-training.txt`.

Start with [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/FILE_MAP.md](docs/FILE_MAP.md).
