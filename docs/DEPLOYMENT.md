# Deployment

No live deployment was performed. Root `render.yaml` and `backend/railway.toml` are preparation files and must be reviewed against the selected provider account before use; they contain no URLs or secrets.

## Deployment stage 1

Set `AI_HEAVY_MODELS_ENABLED=false` and `AI_PREWARM_MODELS=false`. Validate the Next.js frontend, FastAPI backend, authentication, PostgreSQL migrations, Redis, Qdrant, manual meal logging, USDA when configured, ordinary APIs, and health endpoints. Health must report `heavy_models_enabled: false`. Do not install or fetch model artifacts in this stage.

Deploy separate processes for the API (`alembic upgrade head` then Uvicorn), event worker (`python -m app.workers.main`), and frontend. Use managed PostgreSQL, Redis, and a persistent Qdrant deployment. Store secrets only in provider environment settings. Local artifact storage is suitable only with a persistent disk; otherwise configure an S3-compatible artifact provider.

## Staged enablement

1. Stage 1: heavy models false; validate the web platform and manual flows.
2. Stage 2: enable BGE memory in an online environment with adequate memory, then validate it separately.
3. Stage 3: enable the Indian-food classifier only after a verified production artifact exists and every open-set promotion gate passes.
4. Stage 4: evaluate FoodSAM independently.
5. Stage 5: evaluate FoodSeg103 only if evidence shows additional value.

Production startup starts services, may fetch an explicitly promoted artifact, verifies its manifest/checksums, and keeps inference lazy. Startup must never download Kaggle datasets, prepare data, train, evaluate, benchmark, or download experimental datasets. Training images and Kaggle data are not deployment dependencies.

Render preparation defines backend and worker services with both model flags false. Add managed databases, secret environment variables, frontend service, persistent Qdrant, and an artifact backend during provider setup. Railway preparation defines the backend build/start/health configuration; create worker and frontend as separate services and set both flags false in the Railway environment.

Required health checks: `/api/v1/health`, PostgreSQL connectivity through normal API behavior, Redis, Qdrant, and an honest ZenFit AI capability response. Do not enable prewarming during initial rollout.
