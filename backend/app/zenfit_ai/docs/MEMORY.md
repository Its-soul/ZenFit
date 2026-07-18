# Memory Architecture

The research-only 80-class dataset is isolated from production artifacts and from user memory. No private meal images were used for recovery training or rejection evaluation.

Training datasets and classifier artifacts remain outside semantic memory. Kaggle recipe metadata is not ingested into user memory, and no private meal images were used in this run.

Privacy boundary: semantic memory contains user-scoped derived facts; meal corrections are separate; meal image bytes and raw pose video are not memory. Browser pose sends landmarks, not frames.

PostgreSQL owns structured facts. Qdrant stores durable contextual summaries, embedded with BGE-M3 (1024 dimensions), never authoritative records. Greetings and other transient chat are rejected; durable preferences, barriers, goals, recurring patterns, and important changes may be written after similarity-based duplicate prevention.

```text
Behavior/Event -> Structured DB -> Memory candidate -> Importance filter -> BGE-M3 -> Qdrant
Request -> Query embedding -> Qdrant(user_id filter) -> Top 20-30 -> Reranker -> Top 5-8 -> Structured facts -> Final context
```

Payload metadata may include `user_id`, `memory_type`, `category`, `source`, `source_event`, `event_type`, `created_at`, `importance`, `confidence`, `related_entity_id`, and `tags`. `user_id` is mandatory for every read/write. Deletion must use both owner filter and point ID; account deletion should delete all points filtered by owner. Retention should follow the account privacy policy and allow export/deletion.

The old 384d `user_memory` collection remains untouched. Run the restartable backfill script to preserve IDs/payloads and re-embed into `user_memory_v2`. Deterministic IDs and Qdrant upserts make repeats safe. Review external model licenses before deployment: BGE model cards, XGBoost Apache-2.0, Qdrant Apache-2.0, MediaPipe Apache-2.0, and each separately installed FoodSAM/FoodSeg/dataset artifact.

Validated migration statistics on a fresh development stack: 3 safe seeded records scanned and newly migrated on the first run; the second run reported all 3 already migrated and 0 new/failed. The seed option is rejected outside development/test. Normal API retrieval strips vector/reranker scores; authenticated debug search is available only in development/test.
