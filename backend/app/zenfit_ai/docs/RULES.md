# Engineering Rules

- Production activation requires all dataset, license, metric, calibration, non-food, latency, and regression gates to pass.
- Development activation still requires dataset, metric, and calibration gates; a bad research model is not activated merely because it trained.

- Never label a model ready without weights and real inference evidence.
- Correction telemetry is not consent to retain an image for training.
- Do not count pose repetitions when critical landmark visibility is below 0.6.
- Meal image bytes are request-temporary; analysis metadata expires and confirmation is owner-scoped and single-use.

- No paid AI APIs or paid-service dependency.
- No fake predictions, confidence, model availability, or training labels.
- Every Qdrant query must filter by `user_id`; PostgreSQL facts remain source of truth and Qdrant is contextual memory.
- No medical diagnosis or automatic dangerous/high-impact plan changes.
- No silent model failure: status and fallback source must be visible.
- Never commit secrets or create `.env.example` files.
- Keep this package shallow, typed, testable, and use snake_case modules and PascalCase classes.
- Do not use an LLM for numerical prediction.
- Optional models must fail gracefully and load lazily.
- Validate public inputs, use structured schemas, log stages/latency rather than raw sensitive text, and preserve existing clients/event infrastructure.
- Default tests must not download weights; use explicit `integration`, `model`, and `slow` markers.
- Meal analysis IDs are user-owned, expire after one hour, and are single-use after confirmation.
- External FoodSAM/FoodSeg installations must expose a reviewed `zenfit_adapter.py`; a directory alone is never a ready capability.
