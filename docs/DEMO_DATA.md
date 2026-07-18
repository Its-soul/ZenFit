# Demo Data Map

This document lists all demo, mock, sample, seed, fixture, test, generated, and temporary development data found in the repository.

## Summary

There are three real demo/test data systems:

1. Dynamic demo history generation under `backend/app/demo` and `scripts/seed_demo_data.py`.
2. AI evaluation fixtures under `backend/tests/fixtures`.
3. Frontend development defaults and hardcoded navigation/form starter values.

No fake API response files were found.

No `mockData` directory was found.

No frontend chart uses static JSON data; analytics charts call `GET /api/v1/analytics/history`.

## Demo Data Locations Table

| Type | File Path | Used By | Notes |
|---|---|---|---|
| Demo personas | `backend/app/demo/profiles.py` | `backend/app/demo/seeder.py`, `backend/app/demo/simulation.py` | Static list of five demo users and behavior parameters. |
| Demo simulation rules | `backend/app/demo/simulation.py` | `backend/app/demo/seeder.py` | Dynamic deterministic history generation. |
| Demo seed writer | `backend/app/demo/seeder.py` | `scripts/seed_demo_data.py` | Writes PostgreSQL rows and Qdrant memories. |
| Demo seed CLI | `scripts/seed_demo_data.py` | Developer command | Runs demo seeding with `--days`, `--seed`, `--keep-existing`. |
| AI prompt regression dataset | `backend/tests/fixtures/prompt_regression_cases.json` | `backend/tests/evaluation/prompt_tests.py` | Static evaluation cases. |
| Recommendation evaluation dataset | `backend/tests/fixtures/recommendation_cases.json` | `backend/tests/evaluation/recommendation_tests.py` | Static evaluation cases. |
| AI eval runner | `scripts/evaluate_ai.py` | Developer command | Runs all AI eval checks. |
| Coach initial message | `frontend/app/coach/page.js` | `/coach` page | Static starter assistant message only. |
| Coach default memory query | `frontend/app/coach/page.js` | `/coach` page | Static search input default. |
| Navigation items | `frontend/components/layout/AppShell.js` | App shell sidebar | Static route metadata, not fake data. |
| Onboarding defaults/options | `frontend/app/onboarding/page.js` | `/onboarding` page | Static form defaults and select options. |
| Workout form defaults | `frontend/app/workouts/page.js` | `/workouts` page | Static initial form values only. |
| Nutrition form defaults | `frontend/app/nutrition/page.js` | `/nutrition` page | Static initial meal form values only. |
| Sleep form defaults | `frontend/app/sleep/page.js` | `/sleep` page | Static initial sleep form values only. |
| Recovery form defaults | `frontend/app/recovery/page.js` | `/recovery` page | Static initial recovery form values only. |
| Architecture sample paths | `AI_FITNESS_OS_ARCHITECTURE.md` | Documentation only | Contains intended sample folder names, not runtime data. |
| Local docs demo accounts | `docs/local-development.md`, `README.md` | Documentation only | Lists demo seed command and demo account password. |
| Python bytecode | `backend/**/__pycache__/*`, `scripts/__pycache__/*` | Python runtime | Generated dev artifacts, not source demo data. |

## Dynamic Demo Seed Data

### `backend/app/demo/profiles.py`

Purpose:

Defines five realistic demo personas.

Schema:

```python
DemoUserProfile(
    email: str,
    full_name: str,
    persona: str,
    goal: str,
    fitness_level: str,
    training_days: int,
    adherence_level: float,
    sleep_base: float,
    sleep_volatility: float,
    meal_consistency: float,
    fatigue_bias: float,
    workout_focus: str,
    password: str = "DemoPass123!",
)
```

Example records:

```python
email="ava.consistent@demo.fitness"
persona="highly_consistent_athlete"
adherence_level=0.92
```

```python
email="maya.inconsistent@demo.fitness"
persona="adherence_struggles"
adherence_level=0.48
```

Static or dynamic:

- Static persona definitions.
- Dynamically expanded into relational history by the seeder.

Used by:

- `backend/app/demo/seeder.py`
- `backend/app/demo/simulation.py`

### `backend/app/demo/simulation.py`

Purpose:

Generates believable day-by-day history for each persona.

Static data inside:

```python
WORKOUT_TITLES = {
    "Performance Conditioning": [...],
    "Fat Loss Foundation": [...],
    "Consistency Builder": [...],
    "Strength With Recovery Guardrails": [...],
    "Hypertrophy Progression": [...],
}
```

```python
MEAL_NAMES = [
    "Greek yogurt bowl",
    "Chicken rice bowl",
    "Protein smoothie",
    ...
]
```

Generated structure:

```python
DaySimulation(
    day=date,
    workout=dict | None,
    meals=list[dict],
    sleep=dict,
    recovery=dict,
    events=list[dict],
)
```

Examples of generated items:

```json
{
  "title": "Full Body Strength",
  "scheduled_date": "2026-05-14",
  "status": "completed",
  "planned_intensity": "moderate",
  "duration_minutes": 45
}
```

```json
{
  "event_type": "sleep.poor",
  "payload": {
    "duration_hours": 5.4,
    "quality_score": 48
  }
}
```

Static or dynamic:

- Dynamic, deterministic by seed.

Used by:

- `backend/app/demo/seeder.py`

### `backend/app/demo/seeder.py`

Purpose:

Writes demo data to PostgreSQL and Qdrant.

Creates:

- `users`
- `user_profiles`
- `workout_sessions`
- `meals`
- `sleep_logs`
- `recovery_checkins`
- `domain_events`
- `recommendations`
- `recommendation_feedback`
- `ai_weekly_reports`
- Qdrant `user_memory` payloads

Static or dynamic:

- Dynamic generated data.
- Uses deterministic `random.Random(seed)`.

Important behavior:

- Deletes/recreates known demo users by default.
- Deletes demo users' Qdrant memories when resetting.
- Uses `--keep-existing` to skip existing demo users.

Used by:

- `scripts/seed_demo_data.py`

### `scripts/seed_demo_data.py`

Purpose:

CLI for seeding.

Usage:

```bash
python scripts/seed_demo_data.py
python scripts/seed_demo_data.py --days 365
python scripts/seed_demo_data.py --seed 123
python scripts/seed_demo_data.py --keep-existing
```

Example output:

```text
- ava.consistent@demo.fitness / DemoPass123! (highly_consistent_athlete, 180 days)
```

## AI Evaluation Datasets

### `backend/tests/fixtures/prompt_regression_cases.json`

Purpose:

Static prompt regression cases for the coach agent.

Structure:

```json
{
  "name": "case name",
  "message": "user message",
  "context": {},
  "must_include": ["required terms"],
  "must_not_include": ["forbidden terms"]
}
```

Example:

```json
{
  "name": "low_readiness_training_guidance",
  "message": "Should I train hard today?",
  "must_include": ["readiness", "low"],
  "must_not_include": ["max out", "ignore"]
}
```

Used by:

- `backend/tests/evaluation/prompt_tests.py`
- `backend/tests/evaluation/runner.py`
- `scripts/evaluate_ai.py`

### `backend/tests/fixtures/recommendation_cases.json`

Purpose:

Static recommendation quality test cases.

Structure:

```json
{
  "name": "case name",
  "event_type": "workout.missed",
  "context": {},
  "expected_category": "workout",
  "minimum_confidence": 0.8
}
```

Used by:

- `backend/tests/evaluation/recommendation_tests.py`
- `backend/tests/evaluation/runner.py`
- `scripts/evaluate_ai.py`

## Frontend Development Defaults

These are not fake API responses. They are UI defaults, starter messages, or form seed values.

| File | Static Data | Purpose |
|---|---|---|
| `frontend/components/layout/AppShell.js` | `navItems` route array | Sidebar navigation. |
| `frontend/app/onboarding/page.js` | Goal/level/unit options and initial form | Onboarding form defaults. |
| `frontend/app/coach/page.js` | Initial assistant message and default memory query | Starter UX before API response. |
| `frontend/app/workouts/page.js` | New workout form defaults | Faster manual testing. |
| `frontend/app/nutrition/page.js` | Meal form defaults | Faster manual testing. |
| `frontend/app/sleep/page.js` | Sleep form defaults | Faster manual testing. |
| `frontend/app/recovery/page.js` | Recovery form defaults | Faster manual testing. |

## Backend Built-In Defaults That Affect Data

These are not mock datasets, but they create default behavior when real data is missing.

| File | Default | Effect |
|---|---|---|
| `backend/app/modules/workouts/service.py` | Auto-creates today's workout if missing | Dashboard always has a workout. |
| `backend/app/modules/nutrition/service.py` | `calorie_target=2200`, `protein_target_g=150` | Nutrition target defaults. |
| `backend/app/modules/recommendations/service.py` | Starter recommendation if none exists | Ensures dashboard has a recommendation. |
| `backend/app/modules/dashboard/service.py` | Default readiness `82` if no recovery exists | Dashboard fallback. |
| `backend/app/ai/memory/embeddings.py` | Deterministic local embedding | Local vector behavior without paid API. |

## No Fake API Response Files Found

The codebase does not contain:

- `mockData` folder
- `fixtures` folder
- MSW handlers
- JSON fake API response files
- hardcoded frontend analytics JSON
- hardcoded frontend recommendation lists

Runtime UI data is fetched through services in `frontend/services`.

