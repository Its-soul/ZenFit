# Technical and UX Design

Candidate 1.1.0 is not exposed despite high supported-class accuracy because unsupported foods are often forced into known labels. Manual correction remains the safe UX.

The confidence UI continues to use manual fallback. Candidate 1.0.0 is not exposed because model-quality gates failed; low-confidence presentation is not a substitute for an unusable classifier.

Meal review uses plain-language confidence and alternatives, editable quantities/grams, recalculated totals, and a permanent manual fallback. Technical model details and filesystem paths are not exposed.

Service boundaries follow one direction: API → orchestrator → replaceable capability → structured result → existing persistence. Schemas expose explicit confidence, source, warnings, and model availability. Bad files return validation errors; absent optional weights return limited results; external lookup failures request manual entry rather than invented nutrition.

Meal UX shows detected food, quantity, grams, confidence, and warnings, then requires correction/confirmation before saving. Loading UI should identify analysis stages and allow cancellation. Recommendation UI should show triggering factors and whether ranking came from rules or a trained model. Pose UI should show reps, range-of-motion observations, and the non-medical disclaimer. Safety messages replace training advice when a transparent red flag fires.

Models load once per process and only when first used. CPU is the default, CUDA may be selected, USDA responses are cached, MediaPipe landmarks should be extracted client-side, and heavyweight image work should move through the existing worker as demand grows. The architecture stays simple by using one modular monolith, one event bus, one relational database, and one vector database.

Capability states are `ready`, `partial`, `fallback`, and `unavailable`. The UI never describes unavailable recognition as ready. At level 0, a photo may be validated and attached to a secure analysis session, but the user must enter foods manually. Level 1 adds whole-dish classification; level 2 adds regions; level 3 adds ingredients; level 4 combines all three. Current deployment is level 0 until licensed classifier or segmentation weights are installed.
