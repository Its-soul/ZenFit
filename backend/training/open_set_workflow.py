from __future__ import annotations

import hashlib
import json
import math
import os
import random
import statistics
import time
from collections import Counter, defaultdict
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
TRUTHS = {"supported_food", "unknown_food", "non_food"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _images(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES)


def _license_record(manifest: dict) -> dict:
    sources = manifest.get("sources", [manifest])
    source = sources[0] if sources else {}
    return {
        "source": source.get("dataset_id") or source.get("source_url") or source.get("dataset_name"),
        "license": source.get("license"),
        "license_review_status": source.get("license_review_status"),
        "research_only": source.get("license_review_status") != "approved",
    }


def build_evidence_manifest(*, prepared_dataset: Path, raw_food_root: Path, non_food_root: Path, output: Path, per_group: int = 100, seed: int = 42) -> dict:
    split_manifest_path = prepared_dataset / "split_manifest.json"
    if not split_manifest_path.is_file():
        raise FileNotFoundError(f"Prepared split manifest missing: {split_manifest_path}")
    split_manifest = json.loads(split_manifest_path.read_text())
    license_record = _license_record(split_manifest)
    supported_classes = set(split_manifest.get("classes", {}))
    supported_source_classes = {row.get("source_class") for row in split_manifest.get("classes", {}).values() if row.get("source_class")}
    training_hashes = {item.get("sha256") for item in split_manifest.get("files", []) if item.get("sha256")}
    rng = random.Random(seed)

    supported_pool = []
    for class_dir in sorted((prepared_dataset / "test").iterdir()):
        if class_dir.is_dir():
            supported_pool.extend((path, class_dir.name) for path in _images(class_dir))
    rng.shuffle(supported_pool)
    supported = supported_pool[:per_group]

    unknown_pool = []
    for class_dir in sorted(raw_food_root.iterdir()):
        if class_dir.is_dir() and class_dir.name not in supported_classes and class_dir.name not in supported_source_classes:
            unknown_pool.extend((path, class_dir.name) for path in _images(class_dir))
    rng.shuffle(unknown_pool)
    unknown = unknown_pool[:per_group]

    non_food_source_path = non_food_root / "source_manifest.json"
    if not non_food_source_path.is_file():
        raise FileNotFoundError("Non-food source_manifest.json is required; do not invent license evidence")
    non_food_source = json.loads(non_food_source_path.read_text())
    non_food_license = {
        "source": non_food_source.get("source") or non_food_source.get("dataset_id"),
        "license": non_food_source.get("license"),
        "license_review_status": non_food_source.get("license_review_status", "pending"),
        "research_only": non_food_source.get("license_review_status") != "approved",
    }
    non_food_pool = [(path, path.parent.name) for path in _images(non_food_root)]
    rng.shuffle(non_food_pool)
    non_food = non_food_pool[:per_group]

    items, seen = [], set()
    for truth, rows, evidence_license in (("supported_food", supported, license_record), ("unknown_food", unknown, license_record), ("non_food", non_food, non_food_license)):
        for path, class_name in rows:
            digest = sha256(path)
            if digest in seen:
                raise ValueError(f"Duplicate evidence image: {path}")
            if truth != "supported_food" and digest in training_hashes:
                raise ValueError(f"{truth} image overlaps classifier splits: {path}")
            seen.add(digest)
            items.append({"path": str(path.resolve()), "truth": truth, "source": evidence_license["source"], "license": evidence_license["license"], "license_review_status": evidence_license["license_review_status"], "research_only": evidence_license["research_only"], "class_name": class_name, "sha256": digest})
    payload = {"schema_version": 1, "seed": seed, "target_per_group": per_group, "counts": dict(Counter(item["truth"] for item in items)), "limitations": ["Evidence below target remains developer-beta evidence only."] if any(sum(item["truth"] == truth for item in items) < per_group for truth in TRUTHS) else [], "items": items}
    output.parent.mkdir(parents=True, exist_ok=True); output.write_text(json.dumps(payload, indent=2))
    return validate_evidence_manifest(output, split_manifest_path)


def validate_evidence_manifest(path: Path, split_manifest_path: Path) -> dict:
    payload = json.loads(path.read_text()); split_manifest = json.loads(split_manifest_path.read_text())
    split_hashes = defaultdict(set)
    for row in split_manifest.get("files", []):
        split_hashes[Path(row["path"]).parts[0]].add(row.get("sha256"))
    errors, seen, counts = [], set(), Counter()
    for index, item in enumerate(payload.get("items", [])):
        source_path = Path(item.get("path", "")); truth = item.get("truth"); digest = item.get("sha256")
        if truth not in TRUTHS: errors.append(f"item {index}: invalid truth")
        if not source_path.is_file(): errors.append(f"item {index}: file missing")
        if not digest: errors.append(f"item {index}: SHA256 missing")
        elif source_path.is_file() and sha256(source_path) != digest: errors.append(f"item {index}: SHA256 mismatch")
        if digest in seen: errors.append(f"item {index}: duplicate SHA256")
        seen.add(digest); counts[truth] += 1
        if truth == "supported_food" and digest not in split_hashes["test"]: errors.append(f"item {index}: supported evidence is not from test split")
        if truth in {"unknown_food", "non_food"} and any(digest in values for values in split_hashes.values()): errors.append(f"item {index}: overlaps classifier split")
    return {"valid": not errors, "counts": dict(counts), "errors": errors, "manifest": payload if not errors else None}


def load_candidate(candidate: Path, device: str):
    import torch
    from training.train_indian_food import build_classifier_model, build_evaluation_transform

    required = ("model.pt", "classes.json", "config.json", "calibration.json")
    missing = [name for name in required if not (candidate / name).is_file()]
    if missing: raise FileNotFoundError("Candidate incomplete: " + ", ".join(missing))
    classes = json.loads((candidate / "classes.json").read_text()); config = json.loads((candidate / "config.json").read_text()); calibration = json.loads((candidate / "calibration.json").read_text())
    model = build_classifier_model(config["architecture"], len(classes), pretrained=False).to(device)
    model.load_state_dict(torch.load(candidate / "model.pt", map_location=device, weights_only=True)); model.eval()
    return model, classes, config, calibration, build_evaluation_transform(config)


def generate_predictions(*, candidate: Path, evidence_manifest: Path, output: Path, device: str = "cuda") -> dict:
    import torch
    from PIL import Image
    from app.ai.meal_scan.open_set import probability_entropy

    if device == "cuda" and not torch.cuda.is_available(): raise RuntimeError("CUDA is required but unavailable")
    evidence = json.loads(evidence_manifest.read_text()); model, classes, config, calibration, transform = load_candidate(candidate, device); temperature = calibration["temperature"]
    rows = []
    with torch.inference_mode():
        for item in evidence["items"]:
            logits = model(transform(Image.open(item["path"]).convert("RGB")).unsqueeze(0).to(device))[0]
            probabilities = (logits / temperature).softmax(0).cpu(); values, indices = probabilities.topk(min(3, len(classes)))
            top = [{"label": classes[int(index)], "confidence": float(value)} for value, index in zip(values, indices)]
            rows.append({"truth": item["truth"], "expected_label": item.get("class_name") if item["truth"] == "supported_food" else None, "source_path": item["path"], "source_class": item.get("class_name"), "research_only": item.get("research_only", True), "top_candidates": top, "entropy": probability_entropy(probabilities), "top1_top2_margin": top[0]["confidence"] - (top[1]["confidence"] if len(top) > 1 else 0), "food_probability": None, "energy_score": None, "model_version": candidate.name})
    payload = {"schema_version": 1, "model_version": candidate.name, "architecture": config["architecture"], "calibration_temperature": temperature, "predictions": rows}
    output.parent.mkdir(parents=True, exist_ok=True); output.write_text(json.dumps(payload, indent=2)); return payload


def _distribution(rows: list[dict], key: str) -> dict:
    values = sorted(float(row[key]) for row in rows if row.get(key) is not None)
    if not values: return {"count": 0, "mean": None, "median": None, "p05": None, "p95": None}
    percentile = lambda fraction: values[min(len(values) - 1, round((len(values) - 1) * fraction))]
    return {"count": len(values), "mean": statistics.fmean(values), "median": statistics.median(values), "p05": percentile(.05), "p95": percentile(.95)}


def enrich_open_set_evaluation(predictions: Path, thresholds: Path, output: Path) -> dict:
    from app.ai.meal_scan.open_set import OpenSetThresholds
    from training.open_set_evaluation import decide_row, evaluate_rows

    rows = json.loads(predictions.read_text())["predictions"]; selected = OpenSetThresholds.from_json(thresholds); result = evaluate_rows(rows, selected)
    decisions = [decide_row(row, selected).value for row in rows]
    result["evidence_license"] = {"research_only_samples": sum(bool(row.get("research_only")) for row in rows), "production_eligible_samples": sum(not bool(row.get("research_only")) for row in rows)}
    supported_count = result["sample_counts"].get("supported_food", 0)
    result["supported_food"]["acceptance_rate"] = 1 - result["supported_food"]["false_rejection_rate"] if supported_count else None
    result["unknown_food"]["incorrectly_accepted_as_known"] = [row["source_path"] for row, decision in zip(rows, decisions) if row["truth"] == "unknown_food" and decision == "SUPPORTED_FOOD"]
    result["non_food"]["incorrectly_accepted_as_food"] = [row["source_path"] for row, decision in zip(rows, decisions) if row["truth"] == "non_food" and decision == "SUPPORTED_FOOD"]
    for truth in TRUTHS:
        group = [row for row in rows if row["truth"] == truth]
        result.setdefault("distributions", {})[truth] = {"confidence": _distribution([row | {"confidence": row["top_candidates"][0]["confidence"]} for row in group], "confidence"), "entropy": _distribution(group, "entropy"), "margin": _distribution(group, "top1_top2_margin")}
    output.write_text(json.dumps(result, indent=2)); return result


def benchmark_latency(*, candidate: Path, known_images: list[Path], output: Path, runs: int = 50, warmups: int = 10) -> dict:
    import numpy as np
    import torch
    from PIL import Image

    if len(known_images) < runs: raise ValueError(f"At least {runs} known images are required")
    report = {"model_size_bytes": (candidate / "model.pt").stat().st_size, "parameter_memory_bytes": None, "cpu": None, "gpu": None}
    for device in ("cpu", "cuda"):
        if device == "cuda" and not torch.cuda.is_available(): report[device] = {"available": False, "reason": "CUDA unavailable"}; continue
        model, _, _, calibration, transform = load_candidate(candidate, device); temperature = calibration["temperature"]
        tensors = [transform(Image.open(path).convert("RGB")).unsqueeze(0).to(device) for path in known_images[:runs]]; report["parameter_memory_bytes"] = sum(p.numel() * p.element_size() for p in model.parameters())
        with torch.inference_mode():
            for i in range(warmups): model(tensors[i % len(tensors)]) / temperature
        if device == "cuda": torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
        times = []
        with torch.inference_mode():
            for tensor in tensors:
                if device == "cuda": torch.cuda.synchronize()
                started = time.perf_counter(); model(tensor) / temperature
                if device == "cuda": torch.cuda.synchronize()
                times.append((time.perf_counter() - started) * 1000)
        report[device] = {"available": True, "warmups": warmups, "runs": len(times), "mean_ms": statistics.fmean(times), "median_ms": statistics.median(times), "p95_ms": float(np.percentile(times, 95)), "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated() if device == "cuda" else None}
        del model, tensors
        if device == "cuda": torch.cuda.empty_cache()
    output.write_text(json.dumps(report, indent=2)); return report


def developer_beta_readiness(candidate: Path, latency: dict | None, open_set: dict | None = None, *, artifact_verified: bool = False, manual_correction_available: bool = True) -> dict:
    metrics = json.loads((candidate / "metrics.json").read_text()); calibration = json.loads((candidate / "calibration.json").read_text()); manifest = json.loads((candidate / "dataset_manifest.json").read_text())
    sources = manifest.get("sources", [manifest]); checks = {
        "closed_set_accuracy": metrics.get("accuracy", 0) >= .85,
        "macro_f1": metrics.get("macro_f1", 0) >= .85,
        "calibration_ece": calibration.get("ece", 1) <= .10,
        "candidate_integrity": all((candidate / name).is_file() for name in ("model.pt", "classes.json", "config.json", "metrics.json", "calibration.json", "dataset_manifest.json")),
        "license_gate": bool(sources) and all(str(source.get("license_review_status", "")).lower() == "approved" and source.get("commercial_use_allowed") is True for source in sources),
        "basic_latency_evidence": bool(latency and (latency.get("cpu", {}).get("available") or latency.get("gpu", {}).get("available"))),
        "supported_food_inference": bool(open_set and open_set.get("sample_counts", {}).get("supported_food", 0)),
        "confidence_and_top3": bool(open_set and open_set.get("sample_counts", {}).get("supported_food", 0)),
        "manual_correction_available": manual_correction_available,
    }
    if artifact_verified: checks["artifact_integrity"] = True
    return {"status": "DEVELOPER_BETA_READY" if all(checks.values()) else "DEVELOPER_BETA_BLOCKED", "checks": checks, "production_approved": False}


def generate_release_evidence(*, candidate: Path, open_set_report: Path | None, threshold_report: Path | None, latency_report: Path | None, output: Path, artifact_sha256: str | None = None) -> dict:
    metrics = json.loads((candidate / "metrics.json").read_text()); config = json.loads((candidate / "config.json").read_text()); calibration = json.loads((candidate / "calibration.json").read_text()); manifest_path = candidate / "dataset_manifest.json"; manifest = json.loads(manifest_path.read_text())
    read = lambda path: json.loads(path.read_text()) if path and path.is_file() else None
    open_set, thresholds, latency = read(open_set_report), read(threshold_report), read(latency_report)
    historical = {"type": "historical_metadata_comparison", "direct_binary_comparison": False, "production_regression_gate": "BLOCKED", "baseline": {"version": "1.1.0", "accuracy": .8943, "macro_f1": .8974, "top_3_accuracy": .9849}, "candidate": {"accuracy": metrics.get("accuracy"), "macro_f1": metrics.get("macro_f1"), "top_3_accuracy": metrics.get("top_3_accuracy")}}
    readiness = developer_beta_readiness(candidate, latency, open_set)
    source_license = manifest.get("sources", [manifest])
    payload = {"schema_version": 1, "model_version": candidate.name, "architecture": config.get("architecture"), "dataset_version": config.get("dataset_version"), "dataset_manifest_sha256": sha256(manifest_path), "dataset_license_evidence": source_license or None, "training_images": config.get("training_images"), "validation_images": config.get("validation_images"), "test_images": config.get("test_images"), "closed_set_metrics": {"accuracy": metrics.get("accuracy"), "macro_f1": metrics.get("macro_f1"), "top_3_accuracy": metrics.get("top_3_accuracy")}, "calibration": {"temperature": calibration.get("temperature"), "ece": calibration.get("ece"), "brier_score": calibration.get("brier_score")}, "supported_food": open_set.get("supported_food") if open_set else None, "unknown_food": open_set.get("unknown_food") if open_set else None, "non_food": open_set.get("non_food") if open_set else None, "open_set_evidence_counts": open_set.get("sample_counts") if open_set else None, "open_set_evidence_license": open_set.get("evidence_license") if open_set else None, "recommended_thresholds": thresholds.get("thresholds") if thresholds else None, "cpu_latency": latency.get("cpu") if latency else None, "gpu_latency": latency.get("gpu") if latency else None, "artifact_sha256": artifact_sha256, "artifact_sha256_reason": None if artifact_sha256 else "artifact is packaged after release evidence is generated; verify artifact_manifest.json checksums", "missing_evidence_reasons": {"open_set": None if open_set else "open-set evaluation report unavailable", "thresholds": None if thresholds else "threshold report unavailable", "latency": None if latency else "latency report unavailable"}, "regression": historical, "developer_beta": readiness, "production": {"status": "BLOCKED", "approved": False, "reason": "strict production gates require direct regression and complete production evidence"}, "known_limitations": ["Unknown-food and non-food rejection are experimental.", "Manual confirmation and correction remain recommended.", "Historical regression metrics are not a direct same-runtime binary comparison."]}
    output.write_text(json.dumps(payload, indent=2)); return payload


def update_model_card(candidate: Path, release: dict) -> Path:
    classes = json.loads((candidate / "classes.json").read_text()); metrics = release["closed_set_metrics"]; calibration = release["calibration"]
    content = f"""# Indian Food Classifier {candidate.name}\n\n- Status: {release['developer_beta']['status']}\n- Production approved: No\n- Architecture: {release['architecture']}\n- Dataset: {release['dataset_version']}\n- Supported classes: {', '.join(classes)}\n- Accuracy: {metrics['accuracy']}\n- Macro F1: {metrics['macro_f1']}\n- Top-3 accuracy: {metrics['top_3_accuracy']}\n- Calibration temperature: {calibration['temperature']}\n- ECE: {calibration['ece']}\n- Recommended thresholds: {json.dumps(release.get('recommended_thresholds'))}\n\n## Intended use\n\nSingle-user developer-beta meal classification with confidence, top-3 suggestions, and manual correction.\n\n## Open-set performance\n\nSupported: {json.dumps(release.get('supported_food'))}\nUnknown: {json.dumps(release.get('unknown_food'))}\nNon-food: {json.dumps(release.get('non_food'))}\n\n## Limitations\n\n- Unknown-food and non-food rejection remain experimental.\n- This model is not production approved.\n- Users should manually confirm or correct every prediction.\n"""
    path = candidate / "model_card.md"; path.write_text(content); return path
