# Stage 1 Checklist — Deploy ZenFit Without Heavy AI

Allowed states: `READY FOR TEST`, `NOT TESTED`, `PASS`, `FAIL`, `BLOCKED`.

| Check | Status | Evidence / action |
|---|---|---|
| Frontend builds | PASS | ESLint and production Next.js build passed with explicit HTTPS/WSS validation URLs |
| Backend lightweight image builds | PASS | `INSTALL_AI=false` image built; API/worker imports passed without Torch, Transformers, or XGBoost installed |
| AI heavy models disabled | PASS | Stage-1 configs set `AI_HEAVY_MODELS_ENABLED=false` |
| AI prewarming disabled | PASS | Stage-1 configs set `AI_PREWARM_MODELS=false` |
| Gemini removed from required runtime | PASS | Provider file, imports, routes, settings, UI client, and provider tests removed |
| PostgreSQL configured | NOT TESTED | Configure managed `DATABASE_URL` |
| Migrations applied | READY FOR TEST | API startup runs `alembic upgrade head` before Uvicorn |
| Redis configured | NOT TESTED | Configure managed `REDIS_URL` |
| Qdrant configured | NOT TESTED | Configure `QDRANT_URL` and API key when required |
| Backend health responds | NOT TESTED | Verify `/api/v1/health` after deployment |
| Frontend loads | NOT TESTED | Verify the Vercel production URL |
| Frontend reaches backend | NOT TESTED | Verify configured HTTPS API URL and CORS |
| Authentication works | NOT TESTED | Register, login, refresh, and protected-page smoke test |
| Dashboard works | NOT TESTED | Browser smoke test |
| Workouts work | NOT TESTED | Browser/API smoke test |
| Nutrition manual entry works | PASS | Lightweight nutrition service and route contract tests passed |
| USDA works if key configured | NOT TESTED | Validate using provider-managed `USDA_FDC_API_KEY` |
| Meal Scan gracefully falls back to manual mode | PASS | Heavy-disabled pipeline test returns `MODEL_UNAVAILABLE` and manual guidance |
| WebSocket connectivity checked | NOT TESTED | Use configured `wss://` URL in production |
| Worker starts | NOT TESTED | Start separate service with `python -m app.workers.main` |
| No model download occurs | PASS | Lightweight image omits optional AI requirements; heavy/prewarm flags are false |
| No dataset download occurs | PASS | Web and worker startup do not import offline training commands |
| No training occurs | PASS | Training remains under `backend/training` and outside startup |

Online checks intentionally remain `NOT TESTED` until a real Stage-1 deployment exists.
