from typing import Protocol, runtime_checkable


@runtime_checkable
class OpenSetScorer(Protocol):
    """Optional future scorer; the Meal Scan pipeline does not depend on it."""

    def is_available(self) -> bool: ...
    def score(self, classifier_output: dict) -> float | None: ...
