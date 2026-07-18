# Storage

Canonical application storage is deliberately separated:

- PostgreSQL stores users, fitness records, recommendations, events, prediction audits, and meal corrections.
- Redis stores queues, pub/sub, and short-lived Meal Scan analysis state.
- Qdrant stores user-scoped semantic memory.
- `data/uploads/` stores ignored local uploads when enabled.
- `data/raw/`, `data/training/`, and `data/evaluation/` store ignored offline datasets/evidence.
- `data/models/` stores ignored local model metadata/cache.
- `data/artifacts/` stores ignored packaged artifacts when the local backend is selected.

Browser authentication cache remains in frontend-managed local storage. Secrets never belong in browser storage or tracked files.

Training data stays in Kaggle/local generated datasets. Deployment receives code plus a promoted model artifact; it does not need training images.

An artifact contains `model.pt`, `classes.json`, `config.json`, `calibration.json`, `open_set_thresholds.json`, `metrics.json`, `dataset_manifest.json`, `model_card.md`, and generated `artifact_manifest.json`. Packaging is file-only and never deserializes weights. The manifest records model version, development/production environment, byte size, and SHA-256 for every file. Verification rejects missing, corrupted, incomplete, or environment-mismatched packages.

`local` storage is the default. `s3_compatible` is optional and lazily imports `boto3`; no MinIO service is added. Configure `AI_ARTIFACT_STORAGE_BACKEND`, `AI_ARTIFACT_LOCAL_DIR`, and, for remote storage, `AI_ARTIFACT_S3_BUCKET` plus optional `AI_ARTIFACT_S3_ENDPOINT`. Credentials remain provider-managed environment secrets.

Candidate 1.1.0 is not eligible for a production package because open-set gates are blocked. Packaging must occur only after promotion evidence passes; development and production artifacts remain explicitly distinct.
