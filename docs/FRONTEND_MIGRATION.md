# ZenFit Frontend Migration

## Scope

This document tracks the controlled migration from the generated `ZEN-FRONT` visual reference into the production `frontend` Next.js app. The production frontend remains the source of truth for backend integration, routing, auth, environment configuration, and deployment.

## Structure Found

### Existing `frontend`

- Framework: Next.js App Router with JavaScript components.
- Routes: `app/page.js`, `app/dashboard/page.js`, `app/auth/*`, `app/nutrition/*`, `app/workouts/*`, `app/recovery/page.js`, `app/sleep/page.js`, `app/coach/page.js`, `app/analytics/page.js`, `app/settings/page.js`.
- Shared UI: `components/ui`, `components/common`, `components/layout`, `components/landing`, `components/product`.
- API layer: centralized service modules in `services/`, backed by `services/apiClient.js`.
- Auth: `services/authService.js`, `hooks/useAuth.js`, and `lib/authStorage.js`.
- Runtime config: `lib/runtimeConfig.js` reads public API and WebSocket URLs.
- Styling: Tailwind CSS plus global tokens in `app/globals.css`.

### Generated `ZEN-FRONT`

- Framework: Vite React with TypeScript.
- Routing: in-memory view switching in `src/App.tsx`.
- State: mock data and `localStorage` in `src/data/mockData.ts` and `src/App.tsx`.
- Components: dashboard, workouts, nutrition, recovery, progress, trainers, landing, header, sidebar, drawer, footer.
- Asset: animated background video at `ZEN-FRONT/src/MAIN-BG.mp4`.
- Backend status: visual reference only; no real API client or auth flow.

### Backend

- Framework: FastAPI.
- API prefix: `/api/v1`.
- Routers: auth, users, coach, memory, dashboard, workouts, nutrition, sleep, recovery, recommendations, analytics, AI.
- Heavy AI remains disabled through `AI_HEAVY_MODELS_ENABLED=false` and `AI_PREWARM_MODELS=false` unless separately authorized.

## Migration Decisions

- Do not replace `frontend/` with `ZEN-FRONT/`.
- Keep production Next.js routing and the existing service layer.
- Treat `ZEN-FRONT` mock state as visual reference only.
- Copy `ZEN-FRONT/src/MAIN-BG.mp4` into `frontend/public/assets/main-bg.mp4` so the landing page can render it through a stable public path.
- Use real application routes for landing CTAs: `/auth/register` and `/auth/login`.
- Keep billing/pricing copy presentation-only until a backend billing endpoint exists.

## Page Migration Map

| Feature | Existing Frontend File | `ZEN-FRONT` Reference | Backend Endpoint | Auth | Data | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Public landing | `frontend/app/page.js`, `frontend/components/landing/*` | `src/components/LandingView.tsx`, screenshot, `src/MAIN-BG.mp4` | None for public content | No | Static public copy and real route links | Migrated landing hero and public anchors |
| Login | `frontend/app/auth/login/page.js` | Modal/auth entry in generated app only | `/api/v1/auth/login` | No | Token response and user | Preserved, not visually migrated in this slice |
| Register | `frontend/app/auth/register/page.js` | Modal/auth entry in generated app only | `/api/v1/auth/register` | No | Token response and user | Preserved, not visually migrated in this slice |
| Current user | `hooks/useAuth.js`, `services/authService.js` | Mock `localStorage` user | `/api/v1/auth/me` | Yes | User response | Preserved |
| Dashboard | `frontend/app/dashboard/page.js` | `src/components/DashboardView.tsx` | `/api/v1/dashboard/today` | Yes | Daily summary | Pending |
| Workouts | `frontend/app/workouts/page.js` | `src/components/WorkoutsView.tsx` | `/api/v1/workouts/*` | Yes | Sessions and today workout | Pending |
| Nutrition | `frontend/app/nutrition/page.js`, `frontend/app/nutrition/meal-analysis/page.js` | `src/components/NutritionView.tsx` | `/api/v1/nutrition/*` | Yes | Meals, lookup, local image analysis | Pending |
| Recovery | `frontend/app/recovery/page.js` | `src/components/RecoveryView.tsx` | `/api/v1/recovery/*` | Yes | Readiness and check-ins | Pending |
| Sleep | `frontend/app/sleep/page.js` | Recovery view sleep sections | `/api/v1/sleep/logs` | Yes | Sleep logs | Pending |
| Coach | `frontend/app/coach/page.js` | `src/components/AICoachDrawer.tsx` | `/api/v1/coach/messages` | Yes | Coach messages | Pending |
| Analytics | `frontend/app/analytics/page.js` | `src/components/ProgressView.tsx` | `/api/v1/analytics/*` | Yes | Reports and history | Pending |
| Settings | `frontend/app/settings/page.js` | Settings panel in `src/App.tsx` | Auth/profile endpoints as needed | Yes | User profile/settings | Pending |

## Backend Connections

| Frontend Feature | Backend Endpoint | Method | Auth Required | Status |
| --- | --- | --- | --- | --- |
| Register | `/api/v1/auth/register` | POST | No | Existing connection preserved |
| Login | `/api/v1/auth/login` | POST | No | Existing connection preserved |
| Refresh session | `/api/v1/auth/refresh` | POST | No | Existing connection preserved |
| Logout | `/api/v1/auth/logout` | POST | Yes | Existing connection preserved |
| Current user | `/api/v1/auth/me` | GET | Yes | Existing connection preserved |
| Dashboard today | `/api/v1/dashboard/today` | GET | Yes | Existing connection preserved, not visually migrated |
| Workout sessions | `/api/v1/workouts/sessions` | GET/POST | Yes | Existing connection preserved, not visually migrated |
| Today workout | `/api/v1/workouts/today` | GET | Yes | Existing connection preserved, not visually migrated |
| Nutrition today | `/api/v1/nutrition/today` | GET | Yes | Existing connection preserved, not visually migrated |
| Meal create | `/api/v1/nutrition/meals` | POST | Yes | Existing connection preserved, not visually migrated |
| Meal lookup | `/api/v1/nutrition/meals/lookup` | POST | Yes | Existing connection preserved, not visually migrated |
| Local meal analysis | `/api/v1/nutrition/meals/analyze-image-local` | POST | Yes | Existing connection preserved, not visually migrated |
| Confirm analysis | `/api/v1/nutrition/meals/confirm-analysis` | POST | Yes | Existing connection preserved, not visually migrated |
| Sleep logs | `/api/v1/sleep/logs` | GET/POST | Yes | Existing connection preserved, not visually migrated |
| Recovery readiness | `/api/v1/recovery/readiness` | GET | Yes | Existing connection preserved, not visually migrated |
| Recovery check-ins | `/api/v1/recovery/check-ins` | POST | Yes | Existing connection preserved, not visually migrated |
| Recommendations | `/api/v1/recommendations` | GET | Yes | Existing connection preserved, not visually migrated |
| Coach messages | `/api/v1/coach/messages` | POST | Yes | Existing connection preserved, not visually migrated |
| Analytics | `/api/v1/analytics/*` | GET | Yes | Existing connection preserved, not visually migrated |

## Landing Page

- Source asset found at `ZEN-FRONT/src/MAIN-BG.mp4`.
- Production asset copied to `frontend/public/assets/main-bg.mp4`.
- Rendered by `frontend/components/landing/LandingBackgroundVideo.js`.
- `prefers-reduced-motion: reduce` users receive the lightweight static fallback gradient instead of the animated video.
- CTAs route to `/auth/register` and `/auth/login`.
- Public navigation anchors route to real sections: `#features`, `#how-it-works`, `#pricing`, and `#about`.

## Authentication Flow

- Login, registration, refresh, current-user loading, and logout remain in the existing production flow.
- `services/apiClient.js` attaches bearer tokens and retries 401 responses through `/auth/refresh`.
- `hooks/useAuth.js` verifies protected sessions through `/auth/me`; it does not trust only stored local user data.
- This slice did not perform end-to-end auth verification with a running backend session.

## Environment Variables

Required frontend variables:

```env
NEXT_PUBLIC_API_URL=https://your-backend.example/api/v1
NEXT_PUBLIC_WS_URL=wss://your-backend.example/ws
```

Do not commit temporary localhost or deployment verification values.

## Validation Commands

Run from `frontend/`:

```powershell
npm install
npm run lint
npm run build
```

The current migration slice should also be visually checked across desktop, tablet, and mobile because the hero depends on a full-bleed video asset.

## Remaining Limitations

- Full dashboard, auth-page, nutrition, workout, recovery, sleep, coach, analytics, and settings visual migration is still pending.
- No backend contracts were changed.
- No heavy AI models were run.
- Backend-connected user journeys still need real API/session verification after each future page migration.
- `ZEN-FRONT` remains in place as a visual reference and should not be deleted until the full migration is verified.
