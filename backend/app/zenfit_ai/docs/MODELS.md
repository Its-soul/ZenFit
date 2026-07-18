# Model and Service Licenses

Validated 2026-07-18: EfficientNet candidates 0.1.0 and 1.0.0 exist locally. Version 1.0.0 used only the CC0-declared 5000 Indian Cuisines source, but fails the macro-F1 gate and is neither development- nor production-active. USDA live validation is READY. FoodSAM/FoodSeg remain NOT READY because the classifier prerequisite failed.

Validated 2026-07-17: classifier lifecycle exists but dataset/weights do not (**NOT READY**); FoodSAM has no weights or 10-image evidence (**NOT READY**); FoodSeg103 is optional and outside the default path (**NOT READY**); USDA behavior is implemented but no configured key was available for a live test (**PARTIAL**).

| Component | Purpose | Source | License | Location | Required | Setup and commercial-use note |
|---|---|---|---|---|---|---|
| BGE-M3 | 1024d memory embeddings | `BAAI/bge-m3` | MIT | `AI_MODEL_CACHE_DIR` | Core memory | `python -m app.zenfit_ai.scripts.setup_models`; model card permits local use. |
| BGE reranker v2-m3 | Memory relevance ranking | `BAAI/bge-reranker-v2-m3` | Apache-2.0 | model cache | Core retrieval quality | Same setup command. |
| XGBoost | Numeric prediction | XGBoost project | Apache-2.0 | configured JSON paths | Optional | Train only on genuine labels. |
| MediaPipe Tasks | Browser pose landmarks | Google MediaPipe | Apache-2.0 code | Browser package/model cache | Optional frontend | Camera frames remain local; verify model artifact notices when vendoring. |
| FoodSAM | Food segmentation | `jamesjg/FoodSAM` | Apache-2.0 repository/model | `FOODSAM_MODEL_DIR` | Optional | Official stack has CUDA/C++ and legacy MM dependencies; production compatibility must be tested before enabling. |
| FoodSeg103 | Ingredient segmentation | `LARC-CMU-SMU/FoodSeg103-Benchmark-v1` | Apache-2.0 repository | `FOODSEG103_MODEL_DIR` | Optional | Dataset/artifact terms and transitive Recipe1M dependencies require separate verification. |
| EfficientNet-B0 | Indian dish classifier base | Torchvision | BSD-3-Clause | ZenFit `.pt` weights | Optional | ZenFit-trained weights inherit dataset obligations; never redistribute unverified data. |
| USDA FoodData Central | Nutrition lookup | USDA FDC API | US government data; API terms apply | Remote free API, Redis cache | Optional | Configure `USDA_FDC_API_KEY`; confirm current API terms for deployment. |

FoodSAM and FoodSeg103 are not marked operational merely because a directory exists. Their adapters remain unavailable until a compatible inference entrypoint and weights pass a real image test.
