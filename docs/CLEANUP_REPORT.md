# Repository Cleanup Report

## Problems found

The repository had two simultaneously referenced AI roots, training/tests/docs nested inside runtime source, both `tasks` and worker terminology, route registration spread through `main.py`, model binaries inside the application tree, generated caches/build output, duplicated root documentation, unconditional training/heavy-AI dependencies in the API image, and platform boundaries that used inconsistent build contexts.

## Moves and merges

- Merged the newer local AI runtime from `backend/app/zenfit_ai` into the established `backend/app/ai` package.
- Renamed the new memory implementation to `bge_embeddings.py`, `bge_reranker.py`, and `semantic_retriever.py` so the still-used legacy event memory remains explicit and intact.
- Renamed `prediction/` to `app/ai/predictions/`.
- Moved offline training to `backend/training/`.
- Moved operational AI scripts to `backend/scripts/`.
- Moved all nested AI tests to `backend/tests/unit/ai` and `backend/tests/integration/ai`; moved load and evaluation assets under `backend/tests`.
- Moved `app/tasks` to `app/workers`; the commands are `python -m app.workers.main` and `python -m app.workers.scheduler`.
- Moved project-level AI, auth, demo, product, model, dataset, storage, and release documents into `docs/`.
- Moved Railway configuration to `backend/railway.toml`; Render Blueprint configuration remains at root because it references repository build contexts.

## Deleted

- Deleted the old `backend/app/zenfit_ai` directory after reference migration reached zero. Its runtime source was moved, not discarded.
- Deleted generated `__pycache__`, `.pyc`, `.pytest_cache`, `.next`, and `node_modules` directories after validation.
- Deleted empty duplicate `backend/data`, `backend/uploads`, and root `uploads`; canonical generated data is root `data/`.
- Deleted `AI_FITNESS_OS_ARCHITECTURE.md` and `FULL_DOCUMENTATION.md` because their outdated proposed trees and monolithic instructions were superseded by `ARCHITECTURE.md`, `FILE_MAP.md`, focused docs, and current deployment READMEs.
- Deleted `STORAGE_LOCATIONS.md` after its durable concepts were consolidated into `docs/STORAGE.md` and the architecture map.
- Deleted the temporary Railway-only Dockerfile after standardizing Railway Root Directory on `backend/` and reusing `backend/Dockerfile`.
- Deleted the placeholder-only `infra/k8s` tree; it had no manifests, imports, deployment references, or active staging target.
- Deleted the conflicting `backend/.env.example`; root `.env.example` is now the single secret-free template for Docker, frontend public URLs, backend runtime, AI, and artifact configuration.

## Model artifact cleanup

No development or production activation pointer existed. Metadata for versions 0.1.0, 0.2.0, 1.0.0, and 1.1.0 was preserved under ignored `data/models/indian_food/`. Four inactive `model.pt` binaries totaling 65,536,716 bytes were deleted. Dataset provenance, metrics, calibration, configs, model cards, reproducibility, and gate evidence were preserved.

## Dependencies and Docker

`backend/requirements.txt` now contains API/runtime dependencies. Optional heavy inference dependencies live in `requirements-ai.txt`; training/Kaggle/test dependencies live in `requirements-training.txt`. `backend/Dockerfile` is heavy-AI-free by default and installs AI dependencies only with `INSTALL_AI=true`. Backend and frontend `.dockerignore` files exclude datasets, artifacts, tests/training from runtime images, caches, uploads, and secrets.

## Intentionally preserved

- All Alembic migrations and database models.
- Both memory implementations because both have active call sites; their names now describe their roles.
- Existing coaching, analytics, recommendation, nutrition, event, and demo implementations under the canonical AI package.
- Model metadata and dataset/license provenance.
- Root repository scripts for cross-project demo seeding and lightweight evaluation.

## Remaining technical debt

- The legacy Gemini meal-vision provider is still imported by active nutrition service code and was not deleted blindly; decide separately whether to retire it in favor of the local Meal Scan path.
- Real model, device, load, and online deployment validation remain deferred.
- Provider-specific Render/Railway resources, persistent Qdrant, and remote artifact credentials require account-level configuration.
