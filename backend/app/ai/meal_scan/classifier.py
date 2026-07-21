import json
import math

from app.ai.config import get_ai_settings
from app.ai.meal_scan.artifact_loader import materialize_verified_artifact


def calibrated_softmax(logits, temperature: float):
    if temperature <= 0:
        raise ValueError("calibration temperature must be positive")
    return (logits / temperature).softmax(dim=1)


def load_classifier():
    settings = get_ai_settings()
    root, artifact_manifest = materialize_verified_artifact(settings)
    import torch
    from training.train_indian_food import build_classifier_model, build_evaluation_transform

    classes = json.loads((root / "classes.json").read_text(encoding="utf-8"))
    config = json.loads((root / "config.json").read_text(encoding="utf-8"))
    calibration = json.loads((root / "calibration.json").read_text(encoding="utf-8"))
    thresholds = json.loads((root / "open_set_thresholds.json").read_text(encoding="utf-8"))
    if settings.meal_classifier_environment == "production" and thresholds.get("status") != "approved":
        raise RuntimeError("production classifier requires approved open-set thresholds")
    device = settings.device
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    model = build_classifier_model(config["architecture"], len(classes), pretrained=False).to(device)
    model.load_state_dict(torch.load(root / "model.pt", map_location=device, weights_only=True))
    model.eval()
    return {
        "model": model,
        "classes": classes,
        "config": config,
        "calibration": calibration,
        "thresholds": thresholds,
        "transform": build_evaluation_transform(config),
        "device": device,
        "metadata": {"version": artifact_manifest["model_version"], "environment": artifact_manifest["environment"]},
    }


def classify(image, top_k: int = 3) -> dict | None:
    from app.ai.registry import registry

    loaded = registry.get_food_classifier()
    if loaded is None:
        return None
    import torch

    tensor = loaded["transform"](image).unsqueeze(0).to(loaded["device"])
    temperature = float(loaded["calibration"].get("temperature", 1.0))
    with torch.inference_mode():
        probabilities = calibrated_softmax(loaded["model"](tensor), temperature)[0].cpu()
    values, indices = probabilities.topk(min(top_k, len(loaded["classes"])))
    candidates = [{"label": loaded["classes"][int(index)], "confidence": round(float(value), 6)} for value, index in zip(values, indices)]
    confidence = candidates[0]["confidence"]
    top2 = candidates[1]["confidence"] if len(candidates) > 1 else 0
    entropy = -sum(float(value) * math.log(max(float(value), 1e-12)) for value in probabilities)
    return {
        "top1_confidence": confidence,
        "top2_confidence": top2,
        "margin": round(confidence - top2, 6),
        "entropy": round(entropy, 6),
        "top_candidates": candidates,
        "model_version": loaded["metadata"]["version"],
        "model_environment": loaded["metadata"]["environment"],
        "open_set_thresholds": loaded["thresholds"],
    }
