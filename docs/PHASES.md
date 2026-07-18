# Implementation Phases

Recovery phases A-E PASS: diagnostics, acquisition, audit, balanced v2, and baseline/full candidate training completed. Promotion is BLOCKED at rejection; FoodSAM/FoodSeg and CV load remain out of scope until this gate passes.

2026-07-18 build-only open-set stage: decision engine, detector/OOD interfaces, stored-evidence evaluation, threshold analysis, evidence-size gates, checksum artifact packaging, deployment preparation, and static validator were implemented. Heavy model execution, image inference, integration/model/load tests, and deployment validation were deliberately not run. Open-set promotion remains BLOCKED.

Current gate: lifecycle, orchestration, and correction plumbing are implemented. Classifier training, segmentation evaluation, USDA live validation, physical pose validation, and the 100-DAU load run still require external assets or execution evidence.

Each phase uses unit tests plus FastAPI import checks as its base acceptance gate.

1. **AI folder, config, registry, tests — complete.** Goal: lazy local capabilities. Files: core package and registry. Acceptance: optional absence does not break import.
2. **BGE-M3, Qdrant, reranker — complete.** Goal: scoped 1024d retrieval. Files: `memory/`. Test isolation, dimensions, order, duplicate rules, and restartable migration.
3. **Adherence/readiness — complete foundation.** Goal: shadow prediction. Test missing features, bounded values, and fallbacks. PostgreSQL feature extraction needs more production labels/schema alignment.
4. **Recommendation learning — complete foundation.** Deterministic ranking and optional XGBoost loading exist; feedback feature engineering remains.
5. **Meal scanning foundation — complete.** Validation, orchestration, uncertainty, USDA, and confirmation are implemented.
6. **FoodSAM + FoodSeg — partial.** Graceful adapters exist; install compatible local inference packages/weights and bind their entrypoints.
7. **Indian classifier — complete foundation.** EfficientNet loader/trainer exists; licensed project weights remain required.
8. **USDA integration — complete.** Free API search, audit fields, scaling, and Redis cache are implemented.
9. **Pose analysis — complete foundation.** Four exercise state machines and observations are implemented; client landmark extraction remains frontend work.
10. **Safety/evaluation/performance — complete foundation.** Rules and focused tests exist; production calibration and load testing remain.

For every incomplete item, acceptance requires compatible license recording, real artifacts/data, focused tests, and a graceful unavailable state.

## Current capability matrix (validated 2026-07-16)

| Capability | Status | Evidence |
|---|---|---|
| BGE-M3 | READY | CPU model setup and 1024d integration test passed |
| BGE reranker v2-m3 | READY | Realistic relevance integration test passed |
| Qdrant v2 | READY | 1024d collection; 3-record development migration rerun produced 0 duplicates |
| Adherence XGBoost | SHADOW/FALLBACK | Audit row and missed outcome persisted; no trained artifact |
| Readiness/recommendation XGBoost | FALLBACK | Deterministic paths tested; no trained artifacts |
| FoodSAM/FoodSeg103 | OPTIONAL / NOT READY | Compatible external inference adapters and weights not installed |
| Indian classifier | TRAINING REQUIRED | Production training tools ready; no licensed dataset/weights supplied |
| USDA | UNAVAILABLE in current environment | API client/cache implemented; key absent; small reviewed local reference supports correction MVP |
| Meal confirmation | READY | Authenticated upload, user-scoped Redis analysis, correction, persistence, and totals tested |
| Pose backend/frontend | READY / PARTIAL | Backend and frontend builds pass; browser camera requires device validation |
