from __future__ import annotations

import logging
from difflib import get_close_matches
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
NUTRIENT_IDS = {
    "calories_per_100g": {1008, 2047, 2048},
    "protein_per_100g": {1003},
    "fat_per_100g": {1004},
    "carbs_per_100g": {1005},
}


# Values are per 100g from USDA FoodData Central / SR Legacy style entries.
FALLBACK_FOODS: dict[str, dict[str, float | str]] = {
    "whole egg": {"name": "whole egg", "calories_per_100g": 143, "protein_per_100g": 12.56, "carbs_per_100g": 0.72, "fat_per_100g": 9.51},
    "egg white": {"name": "egg white", "calories_per_100g": 52, "protein_per_100g": 10.9, "carbs_per_100g": 0.73, "fat_per_100g": 0.17},
    "chicken breast cooked": {"name": "chicken breast cooked", "calories_per_100g": 165, "protein_per_100g": 31.02, "carbs_per_100g": 0, "fat_per_100g": 3.57},
    "brown rice cooked": {"name": "brown rice cooked", "calories_per_100g": 123, "protein_per_100g": 2.74, "carbs_per_100g": 25.58, "fat_per_100g": 0.97},
    "white rice cooked": {"name": "white rice cooked", "calories_per_100g": 130, "protein_per_100g": 2.69, "carbs_per_100g": 28.17, "fat_per_100g": 0.28},
    "oats": {"name": "oats", "calories_per_100g": 389, "protein_per_100g": 16.89, "carbs_per_100g": 66.27, "fat_per_100g": 6.9},
    "banana": {"name": "banana", "calories_per_100g": 89, "protein_per_100g": 1.09, "carbs_per_100g": 22.84, "fat_per_100g": 0.33},
    "apple": {"name": "apple", "calories_per_100g": 52, "protein_per_100g": 0.26, "carbs_per_100g": 13.81, "fat_per_100g": 0.17},
    "milk": {"name": "milk", "calories_per_100g": 61, "protein_per_100g": 3.15, "carbs_per_100g": 4.8, "fat_per_100g": 3.25},
    "greek yogurt": {"name": "greek yogurt", "calories_per_100g": 59, "protein_per_100g": 10.19, "carbs_per_100g": 3.6, "fat_per_100g": 0.39},
    "cottage cheese": {"name": "cottage cheese", "calories_per_100g": 98, "protein_per_100g": 11.12, "carbs_per_100g": 3.38, "fat_per_100g": 4.3},
    "bread": {"name": "bread", "calories_per_100g": 265, "protein_per_100g": 9.0, "carbs_per_100g": 49.0, "fat_per_100g": 3.2},
    "pasta": {"name": "pasta cooked", "calories_per_100g": 158, "protein_per_100g": 5.8, "carbs_per_100g": 30.86, "fat_per_100g": 0.93},
    "potato": {"name": "potato", "calories_per_100g": 77, "protein_per_100g": 2.05, "carbs_per_100g": 17.49, "fat_per_100g": 0.09},
    "sweet potato": {"name": "sweet potato", "calories_per_100g": 86, "protein_per_100g": 1.57, "carbs_per_100g": 20.12, "fat_per_100g": 0.05},
    "broccoli": {"name": "broccoli", "calories_per_100g": 34, "protein_per_100g": 2.82, "carbs_per_100g": 6.64, "fat_per_100g": 0.37},
    "spinach": {"name": "spinach", "calories_per_100g": 23, "protein_per_100g": 2.86, "carbs_per_100g": 3.63, "fat_per_100g": 0.39},
    "almonds": {"name": "almonds", "calories_per_100g": 579, "protein_per_100g": 21.15, "carbs_per_100g": 21.55, "fat_per_100g": 49.93},
    "peanut butter": {"name": "peanut butter", "calories_per_100g": 588, "protein_per_100g": 25.09, "carbs_per_100g": 19.56, "fat_per_100g": 50.39},
    "olive oil": {"name": "olive oil", "calories_per_100g": 884, "protein_per_100g": 0, "carbs_per_100g": 0, "fat_per_100g": 100},
    "cheddar cheese": {"name": "cheddar cheese", "calories_per_100g": 403, "protein_per_100g": 24.9, "carbs_per_100g": 1.28, "fat_per_100g": 33.14},
    "salmon": {"name": "salmon cooked", "calories_per_100g": 206, "protein_per_100g": 22.1, "carbs_per_100g": 0, "fat_per_100g": 12.35},
    "tuna": {"name": "tuna canned in water", "calories_per_100g": 116, "protein_per_100g": 25.51, "carbs_per_100g": 0, "fat_per_100g": 0.82},
    "tofu": {"name": "tofu firm", "calories_per_100g": 144, "protein_per_100g": 17.27, "carbs_per_100g": 2.78, "fat_per_100g": 8.72},
    "lentils": {"name": "lentils cooked", "calories_per_100g": 116, "protein_per_100g": 9.02, "carbs_per_100g": 20.13, "fat_per_100g": 0.38},
    "black beans": {"name": "black beans cooked", "calories_per_100g": 132, "protein_per_100g": 8.86, "carbs_per_100g": 23.71, "fat_per_100g": 0.54},
    "whey protein": {"name": "whey protein powder", "calories_per_100g": 352, "protein_per_100g": 78.13, "carbs_per_100g": 6.25, "fat_per_100g": 1.56},
    "paneer": {"name": "paneer", "calories_per_100g": 321, "protein_per_100g": 21.43, "carbs_per_100g": 3.57, "fat_per_100g": 25.0},
    "turkey breast": {"name": "turkey breast cooked", "calories_per_100g": 135, "protein_per_100g": 30.13, "carbs_per_100g": 0, "fat_per_100g": 0.74},
    "avocado": {"name": "avocado", "calories_per_100g": 160, "protein_per_100g": 2.0, "carbs_per_100g": 8.53, "fat_per_100g": 14.66},
    "blueberries": {"name": "blueberries", "calories_per_100g": 57, "protein_per_100g": 0.74, "carbs_per_100g": 14.49, "fat_per_100g": 0.33},
    "strawberries": {"name": "strawberries", "calories_per_100g": 32, "protein_per_100g": 0.67, "carbs_per_100g": 7.68, "fat_per_100g": 0.3},
    "quinoa cooked": {"name": "quinoa cooked", "calories_per_100g": 120, "protein_per_100g": 4.4, "carbs_per_100g": 21.3, "fat_per_100g": 1.92},
    "beef cooked": {"name": "beef cooked", "calories_per_100g": 250, "protein_per_100g": 25.93, "carbs_per_100g": 0, "fat_per_100g": 15.41},
}

ALIASES = {
    "egg": "whole egg",
    "eggs": "whole egg",
    "egg whites": "egg white",
    "chicken breast": "chicken breast cooked",
    "rice": "white rice cooked",
    "brown rice": "brown rice cooked",
    "white rice": "white rice cooked",
    "cooked rice": "white rice cooked",
    "greek yoghurt": "greek yogurt",
    "yoghurt": "greek yogurt",
    "yogurt": "greek yogurt",
    "whey": "whey protein",
    "protein powder": "whey protein",
}


class FoodLookupService:
    def __init__(self, *, api_key: str | None = None, timeout_seconds: float = 8.0):
        self.api_key = api_key if api_key is not None else settings.usda_api_key
        self.timeout_seconds = timeout_seconds

    async def search(self, query: str) -> dict | None:
        normalized_query = self._normalize_query(query)
        if not normalized_query:
            return None

        usda_result = await self._search_usda(normalized_query)
        if usda_result:
            usda_result["analysis_method"] = "usda"
            return usda_result

        fallback = self._fallback_search(normalized_query)
        if fallback:
            logger.warning("USDA lookup unavailable or unmatched; using fallback food data", extra={"query": query})
            return {**fallback, "analysis_method": "fallback"}
        return None

    async def _search_usda(self, query: str) -> dict | None:
        if not self.api_key:
            logger.warning("USDA API key is not configured; skipping FoodData Central lookup")
            return None

        payload = {
            "query": query,
            "pageSize": 5,
            "dataType": ["Foundation", "SR Legacy", "Survey (FNDDS)"],
            "sortBy": "dataType.keyword",
            "sortOrder": "asc",
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(USDA_SEARCH_URL, params={"api_key": self.api_key}, json=payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("USDA FoodData Central lookup failed", extra={"query": query, "error": str(exc)})
            return None

        foods = response.json().get("foods") or []
        for food in foods:
            normalized = self._normalize_usda_food(food)
            if normalized:
                return normalized
        return None

    def _normalize_usda_food(self, food: dict[str, Any]) -> dict | None:
        nutrients: dict[str, float] = {}
        for nutrient in food.get("foodNutrients") or []:
            nutrient_id = nutrient.get("nutrientId") or nutrient.get("nutrientNumber")
            value = nutrient.get("value")
            try:
                nutrient_id = int(nutrient_id)
                value = float(value)
            except (TypeError, ValueError):
                continue

            for field, ids in NUTRIENT_IDS.items():
                if nutrient_id in ids and field not in nutrients:
                    nutrients[field] = value

        required = {"calories_per_100g", "protein_per_100g", "carbs_per_100g", "fat_per_100g"}
        if not required.issubset(nutrients):
            return None

        return {
            "name": str(food.get("description") or food.get("lowercaseDescription") or "USDA food").title(),
            "calories_per_100g": nutrients["calories_per_100g"],
            "protein_per_100g": nutrients["protein_per_100g"],
            "carbs_per_100g": nutrients["carbs_per_100g"],
            "fat_per_100g": nutrients["fat_per_100g"],
        }

    def _fallback_search(self, query: str) -> dict | None:
        key = ALIASES.get(query, query)
        if key in FALLBACK_FOODS:
            return dict(FALLBACK_FOODS[key])

        choices = list(FALLBACK_FOODS)
        matches = get_close_matches(key, choices, n=1, cutoff=0.82)
        if matches:
            return dict(FALLBACK_FOODS[matches[0]])
        return None

    @staticmethod
    def _normalize_query(query: str) -> str:
        return " ".join(query.lower().strip().replace(",", " ").split())
