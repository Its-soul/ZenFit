# ZenFit AI Product Requirements

Recovery update: explicit-label v2 data produced 0.898 macro F1, but development and production recognition remain BLOCKED because unknown-food rejection was 24% and the limited non-food gate did not pass.

Execution update (2026-07-18): Kaggle data was acquired and a real classifier was trained, but its 0.048 macro F1 fails release gates. Automatic recognition remains BLOCKED; manual correction remains the supported meal path.

Status (2026-07-17): automatic meal recognition is **NOT READY** without licensed training data and promoted weights. Manual entry, explicit correction, separate confidence dimensions, and opt-in training consent remain required.

## Vision and problem

ZenFit AI turns structured fitness history into private, local-first assistance without making core features dependent on paid AI. Target users are people tracking workouts, nutrition, sleep, and recovery, plus developers operating a small self-hosted deployment.

The system uses only free/open-source models and free APIs in this implementation.

## Features and requirements

- Memory: durable preferences and repeated behavior are embedded with BGE-M3, stored per user in Qdrant, and reranked before use.
- Prediction: XGBoost can predict adherence, readiness, and recommendation acceptance; transparent fallbacks work before real labeled models exist and adherence remains in shadow mode.
- Meal scanning: optional local segmentation and EfficientNet classification lead to conservative portions, USDA nutrition, explicit uncertainty, and mandatory user confirmation.
- Exercise analysis: normalized client-derived landmarks produce rep counts, range-of-motion observations, and tempo-ready timestamps.
- Safety: deterministic red flags prevent aggressive recommendations and provide escalation language.

Functional requirements include authenticated ownership, restartable memory migration, auditable nutrition matches, optional model health, and structured outputs. Non-functional requirements include CPU-first lazy loading, graceful degradation, no secret logging, and operation for roughly 80-100 daily users.

## Success metrics

Measure memory relevance at top 8, cross-user isolation failures (target zero), prediction calibration after labels exist, recommendation acceptance, corrected meal proportion, API latency, and optional-model failure rate.

## Limitations and out of scope

Image-only portions are estimates. Pose observations are not medical analysis. Models are not trained without genuine labels. Diagnosis, emergency response, paid model APIs, automatic dataset redistribution, medical-grade biomechanics, and autonomous high-impact plan changes are out of scope.

Current product behavior: memory retrieval is operational with locally cached BGE models; prediction stays shadow/fallback while append-only outcomes accumulate; meal correction and saving work without recognition, but automatic recognition remains unavailable until licensed weights are installed; browser pose extraction is an MVP requiring camera/device testing.
