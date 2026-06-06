from __future__ import annotations

import base64
import json
import logging
import re
from pathlib import Path
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

PROMPT = """You are a nutrition vision analyst.

Analyze the meal photo and estimate nutrition from visible food only.

Instructions:
- Identify the dish or likely meal name.
- Identify each visible food item, including mixed-plate components.
- Estimate edible portion size in grams for each item.
- Estimate calories, protein_g, carbs_g, and fat_g per item when possible.
- Include Indian foods when present, such as rice, roti, chapati, dal, paneer, chole bhature, dosa, idli, poha, biryani, curd, sabzi, curry, chutney, and salad.
- Use confidence from 0 to 1. Use lower confidence when the image is unclear or portions are uncertain.
- If uncertain, still provide the best reasonable estimate and set needs_user_confirmation to true.
- Return ONLY valid JSON. Do not include markdown.

Required JSON shape:
{
  "meal_name": "paneer rice plate",
  "foods": [
    {
      "name": "paneer curry",
      "grams": 160,
      "calories": 310,
      "protein_g": 15,
      "carbs_g": 12,
      "fat_g": 23,
      "confidence": 0.72
    }
  ],
  "calories": 640,
  "protein_g": 24,
  "carbs_g": 72,
  "fat_g": 28,
  "confidence": 0.72,
  "needs_user_confirmation": true,
  "warnings": ["Portion size is estimated from image only."]
}
"""

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "meal_name": {"type": "string"},
        "foods": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "grams": {"type": "number"},
                    "calories": {"type": "number"},
                    "protein_g": {"type": "number"},
                    "carbs_g": {"type": "number"},
                    "fat_g": {"type": "number"},
                    "confidence": {"type": "number"},
                },
                "required": ["name", "grams"],
            },
        },
        "calories": {"type": "number"},
        "protein_g": {"type": "number"},
        "carbs_g": {"type": "number"},
        "fat_g": {"type": "number"},
        "confidence": {"type": "number"},
        "needs_user_confirmation": {"type": "boolean"},
        "warnings": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["meal_name", "foods", "confidence", "needs_user_confirmation"],
}


class MealVisionError(RuntimeError):
    """Raised when image analysis cannot produce a usable meal estimate."""


class MealVisionConfigurationError(MealVisionError):
    """Raised when the Gemini API key is not configured."""


class MealVisionProviderError(MealVisionError):
    def __init__(self, message: str, *, status_code: int | None = None, response_text: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class GeminiMealVisionService:
    def __init__(self, *, api_key: str | None = None, model: str | None = None, timeout_seconds: float = 20.0):
        self.api_key = api_key if api_key is not None else settings.gemini_api_key
        self.model = model or settings.gemini_vision_model
        self.timeout_seconds = timeout_seconds

    async def analyze_meal(self, image_bytes: bytes, content_type: str) -> dict[str, Any]:
        if not self.api_key:
            logger.error("Gemini API key is not configured")
            raise MealVisionConfigurationError("Gemini API key is not configured")

        logger.warning(
            "Step 4: Gemini meal image analysis starting model=%s content_type=%s image_bytes=%s",
            self.model,
            content_type,
            len(image_bytes),
            extra={"model": self.model, "content_type": content_type, "image_bytes": len(image_bytes)},
        )

        for attempt in range(2):
            try:
                response = await self._call_gemini(image_bytes, content_type)
                logger.warning("Step 5: Raw Gemini response attempt=%s response=%s", attempt + 1, self._redact_response(response))
                analysis = self.validate_response(response)
                logger.warning(
                    "Step 6: Parsed Gemini response attempt=%s meal_name=%s food_count=%s confidence=%s",
                    attempt + 1,
                    analysis["meal_name"],
                    len(analysis["foods"]),
                    analysis["confidence"],
                    extra={
                        "attempt": attempt + 1,
                        "meal_name": analysis["meal_name"],
                        "food_count": len(analysis["foods"]),
                        "confidence": analysis["confidence"],
                    },
                )
                return analysis
            except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                logger.warning("Gemini meal response validation failed", extra={"attempt": attempt + 1, "error": str(exc)})
                if attempt == 1:
                    raise MealVisionError(f"Gemini returned an unusable meal response: {exc}") from exc
            except MealVisionProviderError as exc:
                logger.warning(
                    "Gemini provider error attempt=%s status_code=%s detail=%s",
                    attempt + 1,
                    exc.status_code,
                    str(exc),
                )
                if attempt == 1 or not self._should_retry_provider_error(exc):
                    raise
            except httpx.HTTPError as exc:
                logger.warning("Gemini transport error attempt=%s error=%s", attempt + 1, str(exc))
                if attempt == 1:
                    raise MealVisionProviderError(f"Gemini transport error: {exc}") from exc
        raise MealVisionError("Gemini meal image analysis failed")

    async def detect_food_items(self, image_bytes: bytes, content_type: str) -> list[dict]:
        analysis = await self.analyze_meal(image_bytes, content_type)
        return analysis["foods"]

    async def _call_gemini(self, image_bytes: bytes, content_type: str) -> dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        encoded_image = base64.b64encode(image_bytes).decode("ascii")
        logger.warning("Step 3: Image encoded for Gemini bytes=%s base64_chars=%s", len(image_bytes), len(encoded_image))
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"inline_data": {"mime_type": content_type, "data": encoded_image}},
                        {"text": PROMPT},
                    ],
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseJsonSchema": RESPONSE_SCHEMA,
                "temperature": 0.1,
            },
        }
        logger.warning(
            "Step 4: Gemini request sent model=%s content_type=%s image_bytes=%s",
            self.model,
            content_type,
            len(image_bytes),
        )
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(url, headers={"x-goog-api-key": self.api_key}, json=payload)

        self._store_debug_response(response)
        if response.status_code >= 400:
            message = self._provider_error_message(response)
            logger.error(
                "Gemini request failed status_code=%s response_text=%s",
                response.status_code,
                response.text[:2000],
            )
            raise MealVisionProviderError(message, status_code=response.status_code, response_text=response.text)
        try:
            return response.json()
        except json.JSONDecodeError as exc:
            logger.error("Gemini returned non-JSON response status_code=%s response_text=%s", response.status_code, response.text[:2000])
            raise MealVisionProviderError("Gemini returned a non-JSON response", status_code=response.status_code, response_text=response.text) from exc

    @staticmethod
    def validate_response(response: dict[str, Any] | str) -> dict[str, Any]:
        if isinstance(response, str):
            data = GeminiMealVisionService._loads_json(response)
        else:
            text = (
                response.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text")
            )
            data = GeminiMealVisionService._loads_json(text) if text else response

        raw_items = data.get("foods") or data.get("items") or data.get("detected_items")
        if not isinstance(raw_items, list):
            raise ValueError("Gemini response must contain a foods list")

        foods = []
        for raw_item in raw_items:
            name = str(raw_item.get("name") or raw_item.get("food") or "").strip().lower()
            grams = GeminiMealVisionService._to_float(raw_item.get("grams") or raw_item.get("portion_grams"))
            if not name or grams <= 0 or grams > 5000:
                continue
            food = {"name": name, "grams": round(grams, 1)}
            for field in ("calories", "protein_g", "carbs_g", "fat_g", "confidence"):
                value = GeminiMealVisionService._to_float(raw_item.get(field))
                if value > 0 or (field == "confidence" and field in raw_item):
                    food[field] = round(value, 2)
            foods.append(food)

        if not foods:
            raise ValueError("Gemini response did not contain any valid food items")

        meal_name = str(data.get("meal_name") or data.get("name") or foods[0]["name"]).strip()
        confidence = GeminiMealVisionService._clamp(GeminiMealVisionService._to_float(data.get("confidence"), default=0.55))
        warnings = data.get("warnings") if isinstance(data.get("warnings"), list) else []

        analysis = {
            "meal_name": meal_name or foods[0]["name"],
            "foods": foods,
            "calories": round(GeminiMealVisionService._to_float(data.get("calories"))),
            "protein_g": round(GeminiMealVisionService._to_float(data.get("protein_g")), 1),
            "carbs_g": round(GeminiMealVisionService._to_float(data.get("carbs_g")), 1),
            "fat_g": round(GeminiMealVisionService._to_float(data.get("fat_g")), 1),
            "confidence": confidence,
            "needs_user_confirmation": bool(data.get("needs_user_confirmation", confidence < 0.75)),
            "warnings": [str(warning) for warning in warnings if str(warning).strip()],
        }
        if not analysis["warnings"] and analysis["needs_user_confirmation"]:
            analysis["warnings"].append("Portion size is estimated from image only.")
        return analysis

    @staticmethod
    def _loads_json(value: str | None) -> dict[str, Any]:
        if not value:
            raise ValueError("Gemini response text is empty")
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", value, flags=re.DOTALL)
            if not match:
                raise
            return json.loads(match.group(0))

    @staticmethod
    def _to_float(value: Any, *, default: float = 0) -> float:
        if value is None or value == "":
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _clamp(value: float, *, minimum: float = 0, maximum: float = 1) -> float:
        return round(max(minimum, min(maximum, value)), 2)

    @staticmethod
    def _redact_response(response: dict[str, Any]) -> str:
        text = json.dumps(response, ensure_ascii=True)
        return text[:4000]

    @staticmethod
    def _provider_error_message(response: httpx.Response) -> str:
        try:
            data = response.json()
        except json.JSONDecodeError:
            return f"Gemini request failed with HTTP {response.status_code}: {response.text[:500]}"
        error = data.get("error") if isinstance(data, dict) else None
        if isinstance(error, dict):
            status = error.get("status") or "UNKNOWN"
            message = error.get("message") or "Gemini request failed"
            return f"Gemini request failed with HTTP {response.status_code} {status}: {message}"
        return f"Gemini request failed with HTTP {response.status_code}: {response.text[:500]}"

    @staticmethod
    def _store_debug_response(response: httpx.Response) -> None:
        try:
            debug_dir = Path(settings.local_upload_dir) / "debug"
            debug_dir.mkdir(parents=True, exist_ok=True)
            debug_file = debug_dir / "gemini_last_response.json"
            payload = {
                "status_code": response.status_code,
                "headers": {"content-type": response.headers.get("content-type")},
                "text": response.text[:12000],
            }
            debug_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError as exc:
            logger.warning("Could not store Gemini debug response: %s", exc)

    @staticmethod
    def _should_retry_provider_error(exc: MealVisionProviderError) -> bool:
        return exc.status_code in {408, 429, 500, 502, 503, 504}
