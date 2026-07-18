# Historical Indian Food Model Cards

Model binaries are local/generated artifacts. This source-controlled summary preserves the model cards that previously lived beside inactive binaries in application source.

## Version 0.1.0

- Architecture: EfficientNet-B0
- Dataset version: `kaggle-5000-indian-cuisines-v1-2026-07`
- Classes: 17
- Training/validation/test: 757/154/180
- Macro F1: 0.0508
- ECE: 0.0275
- Weak classes: biryani, chapati, chicken curry, fish curry, idli
- Expected input: one food-focused RGB image
- Unsupported: reliable multi-food localization, exact portions, unseen foods
- Non-food/unknown behavior: conservative confidence/margin rejection, not a dedicated detector
- Promotion: inactive candidate; production requires every license and validation gate

## Version 1.0.0

- Architecture: EfficientNet-B0
- Dataset version: `kaggle-5000-indian-cuisines-v1-2026-07`
- Classes: 17
- Training/validation/test: 757/154/180
- Macro F1: 0.0477
- ECE: 0.0384
- Weak classes: biryani, chapati, chicken curry, fish curry, idli
- Expected input: one food-focused RGB image
- Unsupported: reliable multi-food localization, exact portions, unseen foods
- Non-food/unknown behavior: conservative confidence/margin rejection, not a dedicated detector
- Promotion: inactive candidate; production requires every license and validation gate
