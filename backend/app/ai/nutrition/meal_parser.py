from __future__ import annotations

import re


UNIT_GRAMS = {
    "g": 1,
    "gram": 1,
    "grams": 1,
    "kg": 1000,
    "kilogram": 1000,
    "kilograms": 1000,
    "cup": 150,
    "cups": 150,
    "tbsp": 15,
    "tablespoon": 15,
    "tablespoons": 15,
    "tsp": 5,
    "teaspoon": 5,
    "teaspoons": 5,
    "slice": 30,
    "slices": 30,
    "piece": 50,
    "pieces": 50,
}

PIECE_GRAMS_BY_FOOD = {
    "egg": 50,
    "eggs": 50,
    "whole egg": 50,
    "banana": 118,
    "apple": 182,
    "bread": 30,
}

CONNECTORS = re.compile(r"\s*(?:,|\+|\band\b)\s*", re.IGNORECASE)
ITEM_PATTERN = re.compile(
    r"^\s*(?P<quantity>\d+(?:\.\d+)?|\.\d+)?\s*(?P<unit>g|grams?|kg|kilograms?|cups?|tbsp|tablespoons?|tsp|teaspoons?|slices?|pieces?)?\s*(?P<name>.+?)\s*$",
    re.IGNORECASE,
)


class MealTextParser:
    def parse(self, query: str) -> list[dict]:
        items: list[dict] = []
        for raw_item in CONNECTORS.split(query.strip()):
            parsed = self._parse_item(raw_item)
            if parsed:
                items.append(parsed)
        return items

    def _parse_item(self, text: str) -> dict | None:
        match = ITEM_PATTERN.match(text)
        if not match:
            return None

        name = self._normalize_name(match.group("name"))
        if not name:
            return None

        quantity = float(match.group("quantity") or 1)
        unit = (match.group("unit") or "piece").lower()
        grams = self._to_grams(quantity, unit, name)
        return {"name": name, "grams": round(grams, 1)}

    def _to_grams(self, quantity: float, unit: str, name: str) -> float:
        if unit in {"piece", "pieces"}:
            unit_weight = PIECE_GRAMS_BY_FOOD.get(name, PIECE_GRAMS_BY_FOOD.get(name.rstrip("s"), UNIT_GRAMS[unit]))
            return quantity * unit_weight
        return quantity * UNIT_GRAMS[unit]

    @staticmethod
    def _normalize_name(name: str) -> str:
        cleaned = re.sub(r"\b(of)\b", " ", name.lower())
        return " ".join(cleaned.split())
