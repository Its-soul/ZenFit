# Indian Food Datasets

Validated 2026-07-18. Acquisition uses the official Kaggle CLI and `KAGGLE_API_TOKEN`; raw and prepared data are ignored and never redistributed from this repository.

| Dataset | Kaggle ID | Version | Actual structure | License | Review | Commercial use | Decision |
|---|---|---:|---|---|---|---|---|
| Indian Food 101 | `nehaprabhavalkar/indian-food-101` | 2 | 255-row, 9-column recipe CSV; 0 images | Data files copyright Original Authors | BLOCKED | No approval recorded | METADATA_ONLY; excluded from training |
| 5000 Indian Cuisines with images | `campusx/5000-indian-cuisines-datasetwith-images` | 1 | 4,466 recipe rows and 4,466 flat-folder image files | CC0-1.0 in Kaggle metadata | APPROVED | Yes | PRIMARY_CLASSIFICATION for this experiment |

## Audit and preparation

The image source contained 3,624 SHA-256-unique images, 842 exact duplicate occurrences, 791 perceptual-hash groups, and no corrupt/zero-byte images. Indian Food 101 has no images, so cross-dataset image overlap is zero. Conservative recipe-title patterns produced 1,091 deduplicated images in 17 canonical classes. Five classes with fewer than 15 unique examples were excluded. Four retained classes are `LOW_DATA`.

Split counts and every file's source row, recipe name, and SHA-256 are recorded in ignored `data/training/indian_food/split_manifest.json`. Deduplication occurs before the seeded 70/15/15 split.

## Outcome

The source is legally usable under its declared Kaggle license, but it is not a strong classification corpus: each recipe is generally a distinct variant and canonical labels are inferred from recipe titles. Full model 1.0.0 overfit and achieved only 6.7% test accuracy and 0.048 macro F1. It is therefore not suitable for activation.

## Data-quality recovery (2026-07-18)

| Dataset | Kaggle ID | Structure | License | Production eligibility | Decision |
|---|---|---|---|---|---|
| Food Image Classification Dataset | `harishkumardatalab/food-image-classification-dataset` | 34 explicit class folders, 23,873 images | CC0-1.0 | APPROVED | Production v2 source |
| Indian Food Images Dataset | `iamsouravbanerjee/indian-food-images-dataset` | 80 explicit classes, 4,000 images | `other` | BLOCKED pending exact terms | Research-only; excluded |

The production source audit found 23,395 SHA-unique images, 478 exact duplicates, 6 cross-class exact duplicates, 1,063 perceptual groups, and no corrupt images. The balanced v2 composition contains 3,929 images across 14 explicit classes, 229-300 images per class, and a 1.31 imbalance ratio. Deduplication precedes the seeded split.

```powershell
docker compose exec backend python -m app.zenfit_ai.training.download_kaggle_datasets
docker compose exec backend python -m app.zenfit_ai.training.audit_kaggle_datasets
docker compose exec backend python -m app.zenfit_ai.training.prepare_kaggle_indian_food
```
