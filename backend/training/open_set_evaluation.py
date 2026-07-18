from __future__ import annotations

from collections import Counter
from itertools import product
from typing import Iterable

from app.ai.meal_scan.open_set import Candidate, OpenSetDecision, OpenSetDecisionEngine, OpenSetInput, OpenSetThresholds


TRUTHS = {"supported_food", "unknown_food", "non_food"}


def decide_row(row: dict, thresholds: OpenSetThresholds) -> OpenSetDecision:
    candidates = tuple(Candidate(item["label"], float(item["confidence"])) for item in row.get("top_candidates", []))
    return OpenSetDecisionEngine(thresholds).decide(OpenSetInput(candidates, row.get("entropy"), row.get("food_probability"), row.get("energy_score"), row.get("model_version"), row.get("model_available", True))).decision


def evaluate_rows(rows: Iterable[dict], thresholds: OpenSetThresholds) -> dict:
    rows = list(rows)
    if any(row.get("truth") not in TRUTHS for row in rows):
        raise ValueError("truth must be supported_food, unknown_food, or non_food")
    counts = Counter(row["truth"] for row in rows)
    decisions = [decide_row(row, thresholds) for row in rows]
    supported = [(row, decision) for row, decision in zip(rows, decisions) if row["truth"] == "supported_food"]
    unknown = [decision for row, decision in zip(rows, decisions) if row["truth"] == "unknown_food"]
    nonfood = [decision for row, decision in zip(rows, decisions) if row["truth"] == "non_food"]
    supported_correct = sum(decision is OpenSetDecision.SUPPORTED_FOOD and row.get("expected_label") == row.get("top_candidates", [{}])[0].get("label") for row, decision in supported)
    accepted = {OpenSetDecision.SUPPORTED_FOOD}
    unknown_false_accept = sum(decision in accepted for decision in unknown)
    nonfood_false_accept = sum(decision in accepted for decision in nonfood)
    overall_correct = supported_correct + len(unknown) - unknown_false_accept + len(nonfood) - nonfood_false_accept
    rate = lambda value, total: value / total if total else None
    return {
        "sample_counts": dict(counts),
        "supported_food": {"classification_accuracy": rate(supported_correct, len(supported)), "false_rejection_rate": rate(sum(decision is not OpenSetDecision.SUPPORTED_FOOD for _, decision in supported), len(supported))},
        "unknown_food": {"rejection_rate": rate(len(unknown) - unknown_false_accept, len(unknown)), "false_acceptance_rate": rate(unknown_false_accept, len(unknown))},
        "non_food": {"rejection_rate": rate(len(nonfood) - nonfood_false_accept, len(nonfood)), "false_food_acceptance_rate": rate(nonfood_false_accept, len(nonfood))},
        "overall_open_set_accuracy": rate(overall_correct, len(rows)),
        "decision_counts": dict(Counter(decision.value for decision in decisions)),
        "thresholds": thresholds.to_dict(),
    }


def threshold_sweep(rows: Iterable[dict], model_version: str, confidence_values=(0.4, 0.5, 0.6, 0.7), margin_values=(0.05, 0.1, 0.15), entropy_values=(None, 1.0, 1.5, 2.0)) -> list[dict]:
    rows = list(rows); results = []
    for confidence, margin, entropy in product(confidence_values, margin_values, entropy_values):
        thresholds = OpenSetThresholds(model_version=model_version, status="candidate", supported_food_min_confidence=confidence, unknown_below_confidence=min(0.28, confidence), min_top1_top2_margin=margin, max_entropy=entropy)
        metrics = evaluate_rows(rows, thresholds)
        results.append({"thresholds": thresholds.to_dict(), "metrics": metrics})
    return results
