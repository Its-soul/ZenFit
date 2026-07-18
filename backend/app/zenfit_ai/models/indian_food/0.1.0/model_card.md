# Indian Food Classifier 0.1.0

- Architecture: EfficientNet-B0
- Dataset version: kaggle-5000-indian-cuisines-v1-2026-07
- Classes: 17
- Training/validation/test: 757/154/180
- Macro F1: 0.0508
- ECE: 0.0275
- Weak classes: biryani, chapati, chicken_curry, fish_curry, idli
- Expected input: one food-focused RGB image
- Unsupported: reliable multi-food localization, exact portions, unseen foods
- Non-food/unknown behavior: conservative confidence/margin rejection; not a dedicated detector
- Promotion: candidate; production requires all license and validation gates
