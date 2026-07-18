import asyncio, hashlib, json, re
import httpx
from app.core.redis_client import get_redis_client
from app.zenfit_ai.config import get_ai_settings
from app.zenfit_ai.meal_scan.food_aliases import food_search_name
from app.zenfit_ai.meal_scan.local_nutrition import local_lookup


def normalize_name(name: str) -> str: return re.sub(r"[^a-z0-9 ]", "", name.lower()).strip()


class USDANutritionClient:
    async def lookup(self, name: str, grams: float) -> dict | None:
        settings = get_ai_settings(); normalized = normalize_name(food_search_name(name))
        reviewed_local=local_lookup(name,grams)
        if reviewed_local:return reviewed_local
        if not settings.usda_api_key:return None
        cache_key = "zenfit:usda:" + hashlib.sha256(normalized.encode()).hexdigest()
        try:
            cached = get_redis_client().get(cache_key)
            data = json.loads(cached) if cached else None
        except Exception: data = None
        if data is None:
            try:
                response=None
                async with httpx.AsyncClient(timeout=httpx.Timeout(10,connect=3)) as client:
                    for attempt in range(2):
                        response=await client.get("https://api.nal.usda.gov/fdc/v1/foods/search",params={"api_key":settings.usda_api_key,"query":normalized,"pageSize":10})
                        if response.status_code not in {429,500,502,503,504} or attempt==1:break
                        await asyncio.sleep(.25)
                    response.raise_for_status();foods=response.json().get("foods",[])
                if not foods:return None
                query_words=set(normalized.split())
                def score(food):
                    description=set(normalize_name(food.get("description","")).split())
                    overlap=len(query_words & description)/max(len(query_words),1)
                    return overlap + (.15 if "foundation" in str(food.get("dataType","")).lower() else 0)
                data=max(foods,key=score); data["_zenfit_match_confidence"]=round(min(score(data),1),2)
                try: get_redis_client().setex(cache_key, 86400, json.dumps(data))
                except Exception: pass
            except Exception:return None
        nutrients = {n.get("nutrientName", "").lower(): float(n.get("value") or 0) for n in data.get("foodNutrients", [])}
        factor = grams/100
        def find(*keys): return next((v for k,v in nutrients.items() if any(key in k for key in keys)), 0) * factor
        confidence=float(data.get("_zenfit_match_confidence",.5))
        return {"calories": round(find("energy"),1), "protein_g": round(find("protein"),1), "carbs_g": round(find("carbohydrate"),1), "fat_g": round(find("total lipid", "total fat"),1), "fiber_g": round(find("fiber"),1), "usda_food_id": data.get("fdcId"), "matched_description": data.get("description"), "match_confidence": confidence, "requires_confirmation": confidence < .65}
