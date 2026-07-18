# End-to-End Development Demo

Do not demo candidate 1.1.0 as active recognition. It passes supported-class metrics but fails unknown/non-food release evidence; demonstrate manual fallback until rejection is resolved.

Current demo gate (2026-07-18): do not demonstrate automatic classification. Candidate 1.0.0 failed model-quality promotion. Demonstrate upload validation, honest unavailable state, manual correction, nutrition lookup, and confirmation only.

Check `/ai/health` for an active Indian classifier version before demonstrating automatic recognition. Otherwise demonstrate the honest manual fallback and do not call classifier, FoodSAM, FoodSeg103, or USDA ready.

```bash
docker compose build backend worker
docker compose up -d
docker compose exec backend python -m scripts.setup_models
docker compose exec backend python -m scripts.backfill_memory --seed-development
docker compose exec backend pytest -q
docker compose exec backend pytest -q -m integration
```

Register/login at `/auth/register`. In development, call authenticated `POST /api/v1/ai/memory/debug-search`. Create and miss today's workout to produce a shadow prediction, recommendation, and worker memory. Open `/nutrition/meal-analysis`, upload a JPEG/PNG/WebP, manually add/correct foods when recognition is unavailable, and confirm; `/nutrition` then shows updated totals. Open `/workouts/form-check`, grant camera permission, choose a supported exercise, and observe rep/form output. Camera frames stay on-device.

FoodSAM/FoodSeg external adapter contract: place a reviewed `zenfit_adapter.py` in its configured model directory. It must export `segment(PIL.Image)`. FoodSAM returns items with `bbox` and `confidence`; FoodSeg returns `label` and `confidence`. Do not enable until a real sample-image test passes.
