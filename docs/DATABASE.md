# Database Documentation

## Conceptual Schema

ZenFit uses PostgreSQL as its primary relational database. The schema is normalized to ensure data integrity and to support complex queries for user analytics.

### Core Entities

#### 1. `users`
The central identity table.
- **Fields**: `id` (UUID), `email` (String, Unique), `hashed_password` (String), `is_active` (Boolean), `created_at` (Timestamp).
- **Relationships**: One-to-One with `user_profiles`. One-to-Many with `workout_sessions`, `meals`, `sleep_logs`.

#### 2. `user_profiles`
Stores demographic and goal-oriented data.
- **Fields**: `user_id` (UUID, Foreign Key), `full_name` (String), `fitness_level` (String), `primary_goal` (String), `preferences` (JSONB).
- **Relationships**: Belongs to `users`.

#### 3. `workout_sessions`
Logs user exercise activities.
- **Fields**: `id` (UUID), `user_id` (UUID, Foreign Key), `title` (String), `duration_minutes` (Integer), `intensity` (String), `scheduled_date` (Date), `status` (String).
- **Indexes**: Indexed by `user_id` and `scheduled_date` for fast historical lookups.

#### 4. `meals`
Logs nutritional intake.
- **Fields**: `id` (UUID), `user_id` (UUID, Foreign Key), `name` (String), `calories` (Integer), `protein_g` (Numeric), `carbs_g` (Numeric), `fat_g` (Numeric), `logged_at` (Timestamp).
- **Indexes**: Indexed by `user_id` and `logged_at`.

#### 5. `sleep_logs` & `recovery_checkins`
Tracks rest metrics.
- **Fields**: `id` (UUID), `user_id` (UUID, Foreign Key), `duration_hours` (Numeric), `quality_score` (Integer), `readiness_score` (Integer), `date` (Date).

## Data Flow & Ownership

- **Ownership**: All user-generated records (workouts, meals, sleep) strictly belong to a specific `user_id`. Queries are always scoped to the authenticated user's ID to prevent data leakage.
- **Lifecycle**: Records are created by users, potentially augmented by background processing tasks, and read back for dashboard rendering. Soft-deletes or status flags are used where appropriate to preserve historical analytics.

## Vector Database (Qdrant)

In addition to PostgreSQL, ZenFit utilizes Qdrant to store and query vector embeddings.

- **Purpose**: Enables semantic search and contextual retrieval based on user history and preferences.
- **Data Stored**: Mathematical representations (vectors) of user states, activities, or unstructured text inputs.
- **Privacy**: Embeddings are anonymized or strongly associated with internal user UUIDs. No plain-text personally identifiable information (PII) is stored in the vector indices.

## Migrations

Database schema changes are managed using Alembic.
- Migration scripts are located in `backend/alembic/versions/`.
- Migrations must be run prior to application startup using `alembic upgrade head`.
