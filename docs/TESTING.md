# Testing & Release Procedure

This document outlines the standard testing procedures and release gates required for ZenFit deployment. 

## 1. Automated Testing

The backend implements a comprehensive test suite using `pytest`.

```bash
# Run the fast unit test suite
docker compose exec backend pytest -q

# Run the integration suite
docker compose exec backend pytest -q -m integration
```
Tests are separated by markers (`integration`, `model`, `slow`) to prevent the default suite from making external network calls or downloading heavy model weights.

## 2. Release Checklist

Every release must pass the following manual and automated gates. Allowed states are `PASS`, `FAIL`, `BLOCKED`, and `NOT_APPLICABLE`.

### General Quality Gates
| Gate | Description |
|---|---|
| Dataset Validation | All offline training datasets must be verified (no corruption, duplicates removed, splits clean). |
| Model Quality | The model must meet threshold accuracy on test sets, pass latency constraints, and be properly calibrated. |
| Safety & Regression | The open-set fallback mechanisms, non-food rejection, and unknown-food handling must function safely. |
| Production License | Only CC0 or appropriately licensed sources may be used for models deployed to production. |

### Feature Validations
- **USDA Live Validation**: Search, details, caching, and timeout behaviors must pass.
- **Meal Correction**: Owner-scoped automated tests must pass.
- **Cross-User Privacy**: Automated store ownership tests must verify data isolation.
- **Fallback Verification**: Manual meal path fallback must work effectively without heavy model execution.

## 3. Pre-flight Checks
Before deploying to production (e.g., Stage 1 cloud preparation):
1. Verify `AI_HEAVY_MODELS_ENABLED` is correctly set.
2. Confirm no legacy cloud vision dependencies are required.
3. Validate that deployment configurations (`render.yaml`, `railway.toml`) point to the correct static asset paths.
