# Stage 1 Environment Checklist

Store values in the deployment provider, never in source control. Stage 1 does not need dataset, training, or model-download credentials.

## Frontend / Vercel

| Variable | Required | Notes |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Yes | Public HTTPS backend URL including `/api/v1` |
| `NEXT_PUBLIC_WS_URL` | Yes | Public `wss://` backend URL including `/ws` |

## Backend API

| Variable | Required | Notes |
|---|---|---|
| `APP_ENV` | Yes | Set to `production` |
| `DATABASE_URL` | Yes | Managed PostgreSQL SQLAlchemy URL |
| `REDIS_URL` | Yes | Managed Redis URL |
| `QDRANT_URL` | Yes | Managed/external Qdrant URL |
| `QDRANT_API_KEY` | Provider-dependent | Required when the Qdrant service enforces API-key authentication |
| `JWT_SECRET_KEY` | Yes | Strong provider-managed secret |
| `BACKEND_CORS_ORIGINS` | Yes | Exact comma-separated Vercel production origins; never `*` |
| `BACKEND_CORS_ORIGIN_REGEX` | No | Narrow regex for approved preview origins only |
| `USDA_FDC_API_KEY` | No | Enables live USDA lookup; local/manual fallback remains available |
| `LOCAL_UPLOAD_DIR` | No | Defaults to `uploads`; ephemeral on basic cloud instances |
| `AI_HEAVY_MODELS_ENABLED` | Yes | Must be `false` in Stage 1 |
| `AI_PREWARM_MODELS` | Yes | Must be `false` in Stage 1 |
| `AI_ARTIFACT_STORAGE_BACKEND` | Yes | Use `local` in Stage 1; no model is activated |

## Worker

| Variable | Required | Notes |
|---|---|---|
| `APP_ENV` | Yes | Set to `production` |
| `DATABASE_URL` | Yes | Same PostgreSQL service as API |
| `REDIS_URL` | Yes | Same Redis service as API |
| `QDRANT_URL` | Yes | Same Qdrant service as API |
| `QDRANT_API_KEY` | Provider-dependent | Match API configuration |
| `JWT_SECRET_KEY` | Yes | Required by the shared settings loader |
| `AI_HEAVY_MODELS_ENABLED` | Yes | Must be `false` |
| `AI_PREWARM_MODELS` | Yes | Must be `false` |

## Image build

| Variable | Required | Notes |
|---|---|---|
| `INSTALL_AI` | Yes | Keep Docker build argument `false` for Stage 1 |

## Training only — not deployed

| Variable | Notes |
|---|---|
| `KAGGLE_API_TOKEN` | Offline dataset acquisition only |

## Future artifact storage — not required in Stage 1

The code supports `AI_ARTIFACT_STORAGE_BACKEND`, `AI_ARTIFACT_LOCAL_DIR`, `AI_ARTIFACT_S3_BUCKET`, and `AI_ARTIFACT_S3_ENDPOINT`. Do not configure a production model artifact until a later promotion stage passes.
