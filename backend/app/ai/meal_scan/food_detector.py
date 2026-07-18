from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class FoodDetectorResult:
    available: bool
    food_probability: float | None = None


@runtime_checkable
class FoodDetector(Protocol):
    def is_available(self) -> bool: ...
    def predict(self, image: object) -> FoodDetectorResult: ...


class UnavailableFoodDetector:
    def is_available(self) -> bool:
        return False

    def predict(self, image: object) -> FoodDetectorResult:
        return FoodDetectorResult(available=False)
