# Developer-beta meal classifier deployment preparation

This procedure installs and selects the already-trained `1.2.0-colab-candidate` package. It does not promote it to production and never writes `active.json`.

## Artifact layout

Store the intact verified package under this key prefix:

```text
meal-classifier/1.2.0-colab-candidate/
  artifact_manifest.json
  model.pt
  classes.json
  config.json
  calibration.json
  open_set_thresholds.json
  metrics.json
  dataset_manifest.json
  release_evidence.json
  model_card.md
```

For S3-compatible storage, configure the backend environment locally and run from `backend/`:

```powershell
$env:AI_ARTIFACT_STORAGE_BACKEND='s3_compatible'
$env:AI_ARTIFACT_S3_BUCKET='<bucket>'
$env:AI_ARTIFACT_S3_ENDPOINT='<endpoint-if-required>'
python -m scripts.upload_meal_classifier_artifact <artifact-directory> --version 1.2.0-colab-candidate --environment developer-beta
```

Standard AWS credential environment variables are consumed by `boto3`; do not place credentials in Git or command output. The uploader verifies all package checksums first and uploads `artifact_manifest.json` last.

For local development only, copy the complete package to `AI_ARTIFACT_LOCAL_DIR/meal-classifier/1.2.0-colab-candidate`. Render must use object storage because its filesystem is ephemeral.

## Backend build and runtime configuration

Set these on the Render web service, not the worker:

```text
INSTALL_MEAL_CLASSIFIER=true
INSTALL_AI=false
AI_MEAL_CLASSIFIER_ENABLED=true
AI_MEAL_CLASSIFIER_VERSION=1.2.0-colab-candidate
AI_MEAL_CLASSIFIER_ENVIRONMENT=developer-beta
AI_MEAL_CLASSIFIER_ARTIFACT_PREFIX=meal-classifier
AI_ARTIFACT_STORAGE_BACKEND=s3_compatible
AI_ARTIFACT_S3_BUCKET=<bucket>
AI_ARTIFACT_S3_ENDPOINT=<endpoint-if-required>
AWS_ACCESS_KEY_ID=<runtime secret>
AWS_SECRET_ACCESS_KEY=<runtime secret>
AWS_DEFAULT_REGION=<provider region>
AI_DEVICE=cpu
AI_HEAVY_MODELS_ENABLED=false
AI_PREWARM_MODELS=false
```

Render passes Docker-service environment variables through as Docker build arguments, so `INSTALL_MEAL_CLASSIFIER=true` activates the matching Dockerfile `ARG`. Keep artifact credentials runtime-only secrets; the Dockerfile does not reference them during the build.

The classifier is lazy-loaded on the first analysis. Health checks verify and cache the package without constructing the PyTorch model. FoodSAM, FoodSeg, BGE embeddings, and reranking remain disabled.

## Manual verification

1. Verify `GET /api/v1/health` returns `ai.meal_scan.meal_classifier.enabled=true`, `available=true`, the selected version, and `environment=developer-beta`.
2. Sign in and verify `GET /api/v1/ai/health` reports the same capability.
3. Send an authenticated JPEG, PNG, or WebP multipart upload to `POST /api/v1/nutrition/meals/analyze-image-local` using form field `file`.
4. Confirm the response contains `recognition_decision`, `predicted_class`, `confidence`, `top_candidates`, `model_version`, and `model_environment`.
5. Test known, unknown-food, non-food, and manual correction/save paths before enabling frontend traffic.

## Capacity and rollback

CPU PyTorch, torchvision, FastAPI, and the existing backend share one process. A 512 MB Render Free or Starter instance has little safety margin and is not recommended for this integration. Start with at least a 2 GB Standard instance, measure resident memory and p95 latency with real uploads, and move inference to a dedicated service if memory or latency is unstable.

Rollback does not require deleting artifacts. Set `AI_MEAL_CLASSIFIER_ENABLED=false` and redeploy; Meal Scan returns `MODEL_UNAVAILABLE` while manual entry remains available. To roll back to another verified developer-beta package, change only `AI_MEAL_CLASSIFIER_VERSION` and redeploy. Do not create or modify `active.json`.
