from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
import json
import math
from pathlib import Path
from typing import Iterable


class OpenSetDecision(StrEnum):
    SUPPORTED_FOOD = "SUPPORTED_FOOD"
    UNKNOWN_FOOD = "UNKNOWN_FOOD"
    NON_FOOD = "NON_FOOD"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"


@dataclass(frozen=True)
class OpenSetThresholds:
    model_version: str
    status: str = "experimental"
    supported_food_min_confidence: float = 0.57
    unknown_below_confidence: float = 0.28
    min_top1_top2_margin: float = 0.10
    max_entropy: float | None = None
    food_detector_threshold: float | None = None
    energy_score_max: float | None = None

    def __post_init__(self):
        if self.status not in {"experimental", "candidate", "approved"}:
            raise ValueError("threshold status must be experimental, candidate, or approved")
        for name in ("supported_food_min_confidence", "unknown_below_confidence", "min_top1_top2_margin"):
            if not 0 <= getattr(self, name) <= 1:
                raise ValueError(f"{name} must be between 0 and 1")
        if self.unknown_below_confidence > self.supported_food_min_confidence:
            raise ValueError("unknown threshold cannot exceed supported-food threshold")

    @classmethod
    def from_json(cls, path: Path) -> "OpenSetThresholds":
        return cls(**json.loads(path.read_text(encoding="utf-8")))

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Candidate:
    label: str
    confidence: float


@dataclass(frozen=True)
class OpenSetInput:
    top_candidates: tuple[Candidate, ...] = ()
    entropy: float | None = None
    food_probability: float | None = None
    energy_score: float | None = None
    model_version: str | None = None
    model_available: bool = True


@dataclass(frozen=True)
class OpenSetResult:
    decision: OpenSetDecision
    label: str | None
    confidence: float | None
    reason_codes: tuple[str, ...]
    model_version: str | None
    top_candidates: tuple[Candidate, ...] = ()

    def to_dict(self, *, include_debug: bool = False) -> dict:
        result = {
            "decision": self.decision.value,
            "label": self.label,
            "confidence": self.confidence,
            "reason_codes": list(self.reason_codes),
            "model_version": self.model_version,
            "top_candidates": [asdict(item) for item in self.top_candidates],
        }
        return result


def probability_entropy(probabilities: Iterable[float]) -> float:
    values = [float(value) for value in probabilities]
    return -sum(value * math.log(max(value, 1e-12)) for value in values)


class OpenSetDecisionEngine:
    """Pure decision layer. It consumes evidence and never loads or runs a model."""

    def __init__(self, thresholds: OpenSetThresholds):
        self.thresholds = thresholds

    def decide(self, evidence: OpenSetInput) -> OpenSetResult:
        candidates = tuple(sorted(evidence.top_candidates, key=lambda item: item.confidence, reverse=True))
        if not evidence.model_available or not candidates:
            return OpenSetResult(OpenSetDecision.MODEL_UNAVAILABLE, None, None, ("classifier_unavailable",), evidence.model_version)
        top1 = candidates[0]
        top2 = candidates[1].confidence if len(candidates) > 1 else 0.0
        margin = top1.confidence - top2
        threshold = self.thresholds
        if threshold.food_detector_threshold is not None and evidence.food_probability is not None and evidence.food_probability < threshold.food_detector_threshold:
            return OpenSetResult(OpenSetDecision.NON_FOOD, None, top1.confidence, ("food_detector_below_threshold",), evidence.model_version, candidates)
        if top1.confidence < threshold.unknown_below_confidence:
            return OpenSetResult(OpenSetDecision.UNKNOWN_FOOD, None, top1.confidence, ("top1_below_unknown_threshold",), evidence.model_version, candidates)
        reasons = []
        if top1.confidence < threshold.supported_food_min_confidence: reasons.append("top1_below_supported_threshold")
        if margin < threshold.min_top1_top2_margin: reasons.append("margin_below_threshold")
        if threshold.max_entropy is not None and evidence.entropy is not None and evidence.entropy > threshold.max_entropy: reasons.append("entropy_above_threshold")
        if threshold.energy_score_max is not None and evidence.energy_score is not None and evidence.energy_score > threshold.energy_score_max: reasons.append("energy_above_threshold")
        if reasons:
            return OpenSetResult(OpenSetDecision.LOW_CONFIDENCE, None, top1.confidence, tuple(reasons), evidence.model_version, candidates)
        return OpenSetResult(OpenSetDecision.SUPPORTED_FOOD, top1.label, top1.confidence, ("top1_above_threshold", "margin_above_threshold"), evidence.model_version, candidates)
