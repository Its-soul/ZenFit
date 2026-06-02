from __future__ import annotations

import base64
import json
import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

PROMPT = """Identify all food items visible in this meal photo.

Estimate the weight of each food item in grams.

Return ONLY valid JSON.

Example:
{
  "items": [
    {"name": "chicken breast", "grams": 150},
    {"name": "white rice", "grams": 180}
  ]
}
"""

RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "items": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING"},
                    "grams": {"type": "NUMBER"},
                },
                "required": ["name", "grams"],
            },
        }
    },
    "required": ["items"],
}


class GeminiMealVisionService:
    def __init__(self, *, api_key: str | None = None, model: str | None = None, timeout_seconds: float = 20.0):
        self.api_key = api_key if api_key is not None else settings.gemini_api_key
        self.model = model or settings.gemini_vision_model
        self.timeout_seconds = timeout_seconds

    async def detect_food_items(self, image_bytes: bytes, content_type: str) -> list[dict]:
        if not self.api_key:
            logger.warning("Gemini API key is not configured")
            return []

        for attempt in range(2):
            try:
                response = await self._call_gemini(image_bytes, content_type)
                return self.validate_response(response)
            except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                logger.warning("Gemini meal response validation failed", extra={"attempt": attempt + 1, "error": str(exc)})
                if attempt == 1:
                    return []
            except httpx.HTTPError as exc:
                logger.warning("Gemini Vision API request failed", extra={"attempt": attempt + 1, "error": str(exc)})
                return []
        return []

    async def _call_gemini(self, image_bytes: bytes, content_type: str) -> dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": PROMPT},
                        {"inlineData": {"mimeType": content_type, "data": base64.b64encode(image_bytes).decode("ascii")}},
                    ],
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": RESPONSE_SCHEMA,
                "temperature": 0.1,
            },
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(url, params={"key": self.api_key}, json=payload)
            response.raise_for_status()
            return response.json()

    @staticmethod
    def validate_response(response: dict[str, Any] | str) -> list[dict]:
        if isinstance(response, str):
            data = json.loads(response)
        else:
            text = (
                response.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text")
            )
            data = json.loads(text) if text else response

        raw_items = data.get("items")
        if not isinstance(raw_items, list):
            raise ValueError("Gemini response must contain an items list")

        items = []
        for raw_item in raw_items:
            name = str(raw_item.get("name", "")).strip().lower()
            grams = float(raw_item.get("grams", 0))
            if not name or grams <= 0 or grams > 5000:
                raise ValueError("Gemini item has invalid name or grams")
            items.append({"name": name, "grams": round(grams, 1)})
        return items
