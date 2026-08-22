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

## Documentation

- [High-Level Design (HLD)](docs/HLD.md)
- [Low-Level Design (LLD)](docs/LLD.md)
- [API Documentation](docs/API.md)
- [Database Schema](docs/DATABASE.md)
- [Security](docs/SECURITY.md)

## Core Capabilities

- **Frontend**: Next.js website for user interaction.
- **Backend**: FastAPI core providing robust data services.
- **Data Layer**: PostgreSQL, Redis, and Qdrant.

