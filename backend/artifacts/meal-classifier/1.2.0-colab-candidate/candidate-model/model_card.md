# Indian Food Classifier 1.2.0-colab-candidate

- Architecture: EfficientNet-B0
- Dataset version: food-image-classification-cc0-balanced-v2-2026-07
- Classes: 14
- Training/validation/test: 2747/586/596
- Macro F1: 0.8970
- ECE: 0.0225
- Weak classes: naan, chapati, chicken_curry, pav_bhaji, omelette
- Expected input: one food-focused RGB image
- Unsupported: reliable multi-food localization, exact portions, unseen foods
- Non-food/unknown behavior: conservative confidence/margin rejection; not a dedicated detector
- Promotion: candidate; production requires all license and validation gates
