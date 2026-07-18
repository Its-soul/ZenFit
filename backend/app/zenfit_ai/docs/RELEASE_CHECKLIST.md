# AI Release Checklist

Recovery evidence (2026-07-18): pipeline diagnostic PASS; tiny overfit PASS; explicit-label v2 dataset quality PASS; 0.2.0 baseline PASS; 1.1.0 metric/calibration/license/latency/regression PASS; non-food and unknown-food rejection BLOCKED; development and production promotion BLOCKED.

Allowed states are `PASS`, `FAIL`, `BLOCKED`, and `NOT_APPLICABLE`. Evidence belongs in the final column; an unchecked item is `BLOCKED`.

| Gate | Status | Evidence |
|---|---|---|
| Kaggle authentication available | PASS | Both named datasets downloaded |
| Dataset download completed | PASS | Manifests show READY |
| Dataset manifest present for every source | PASS | Two raw manifests |
| Dataset source recorded | PASS | Kaggle IDs and URLs recorded |
| Dataset license recorded | PASS | copyright-authors and CC0-1.0 |
| Dataset license reviewed | PASS | Per-source decisions recorded |
| Commercial-use decision recorded | PASS | Food 101 false; image source true |
| Redistribution decision recorded | PASS | Per-source decision recorded |
| Corrupt-image audit completed | PASS | 0 corrupt images |
| Exact-duplicate audit completed | PASS | 842 duplicate occurrences |
| Near-duplicate audit completed | PASS | 791 perceptual groups |
| Cross-dataset duplicate audit completed | PASS | 0; Food 101 has no images |
| Split-leakage audit completed | PASS | SHA and perceptual dedup before split |
| Class normalization completed | PASS | 17 conservative canonical labels |
| Class-count validation completed | PASS | 13 READY, 4 LOW_DATA, 5 excluded |
| Train/validation/test split completed | PASS | 1,091 images, seeded 70/15/15 |
| Smoke training completed | PASS | Immutable 0.1.0, smoke-only |
| Full training completed | PASS | Immutable 1.0.0, early stopped at epoch 7 |
| Metrics generated | PASS | Test metrics for 180 samples |
| Calibration evaluated | PASS | Validation temperature, test ECE/Brier |
| Model card generated | PASS | Version-local model_card.md |
| Model version created | PASS | 0.1.0 and 1.0.0 retained |
| Promotion gates evaluated | FAIL | Metric/non-food/latency/regression blocked |
| Production-license gate passed | PASS | Only CC0 source used in training |
| Non-food rejection tested | BLOCKED | Await model |
| Unknown-food handling tested | BLOCKED | Await model |
| USDA live validation passed | PASS | Search/details/cache/error/timeout passed |
| Meal correction tested | PASS | Automated owner-scoped store tests |
| Meal confirmation tested | PASS | Integration suite |
| Cross-user ownership tested | PASS | Automated store ownership test |
| Latency measured | BLOCKED | Await classifier |
| RAM measured | BLOCKED | Await classifier |
| Fallback tested | PASS | Manual meal path tests |
| Documentation updated | PASS | Nine documents plus this checklist updated |
