# Open-Set Evaluation

Status: implementation ready; real-model evaluation was not executed locally in this build-only stage.

ZenFit must distinguish `SUPPORTED_FOOD`, `UNKNOWN_FOOD`, `NON_FOOD`, `LOW_CONFIDENCE`, and `MODEL_UNAVAILABLE`. The pure `OpenSetDecisionEngine` consumes stored top candidates, entropy, optional food probability, optional energy score, model version, and versioned thresholds. It never runs EfficientNet.

Candidate 1.1.0 thresholds are experimental: supported confidence 0.57, unknown below 0.28, and minimum top-1/top-2 margin 0.10. They are not production-approved. Entropy, detector, and energy thresholds remain unset until reviewed online evidence exists.

Future evidence belongs under ignored `data/evaluation/open_set/` with a manifest and three logical groups: `supported_food`, `unknown_food`, and `non_food`. Supported data must cover the 14 known classes. Unknown food must cover legally usable food classes outside those classes. Non-food must span objects, rooms, people, electronics, books, animals, vehicles, and varied scenes. Record source, license, class/category, checksum, split, and consent/provenance for every image. Do not commit private images.

The project release gate defaults require 140 supported samples, 5 unknown-food classes and 100 images, plus 6 non-food categories and 100 images. These are configurable project gates, not scientific universal constants. The current 25 unknown-food and 4 non-food probes are insufficient.

Online workflow:

```text
Run inference once in an authorized online model job
-> save prediction_evidence.json
-> run evaluate_open_set.py
-> run analyze_open_set_thresholds.py repeatedly on stored evidence
-> review thresholds and evidence provenance
-> write approved open_set_thresholds.json only after release review
-> attempt promotion
```

The evaluation reports supported classification accuracy/false rejection, unknown rejection/false acceptance, non-food rejection/false-food acceptance, overall open-set accuracy, sample counts, and confidence/margin/entropy sweeps.
