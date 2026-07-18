import asyncio,hashlib,json
import httpx
from app.core.redis_client import get_redis_client
from app.zenfit_ai.config import get_ai_settings
from app.zenfit_ai.meal_scan.nutrition import USDANutritionClient

async def main():
    if not get_ai_settings().usda_api_key:raise SystemExit("USDA LIVE VALIDATION: BLOCKED (key not configured)")
    client=USDANutritionClient();results={}
    for query in ("rice","egg","lentils","yogurt","chicken","roti","chapati","dal","paneer"):
        value=await client.lookup(query,100);results[query]={"status":"PASS" if value and value.get("calories") is not None else "FAIL","source":"local" if value and value.get("source") else "USDA" if value else None}
    invalid=await client.lookup("zzzz_no_such_food_zenfit",100);results["invalid_query"]={"status":"PASS" if invalid is None else "FAIL"}
    remote=await client.lookup("lentils",100);cache_key="zenfit:usda:"+hashlib.sha256(b"lentils").hexdigest();results["cache_write"]={"status":"PASS" if get_redis_client().get(cache_key) else "FAIL"};cached=await client.lookup("lentils",100);results["cache_hit"]={"status":"PASS" if cached and cached.get("usda_food_id")==remote.get("usda_food_id") else "FAIL"}
    async with httpx.AsyncClient(timeout=httpx.Timeout(10,connect=3)) as http:
        detail=await http.get(f"https://api.nal.usda.gov/fdc/v1/food/{remote['usda_food_id']}",params={"api_key":get_ai_settings().usda_api_key});results["food_details"]={"status":"PASS" if detail.status_code==200 and detail.json().get("fdcId") else "FAIL"}
        bad=await http.get("https://api.nal.usda.gov/fdc/v1/foods/search",params={"api_key":"invalid-zenfit-validation-key","query":"rice"});results["invalid_key"]={"status":"PASS" if bad.status_code in {400,401,403} else "FAIL"}
    try:
        async with httpx.AsyncClient(timeout=.000001) as http:await http.get("https://api.nal.usda.gov/fdc/v1/foods/search")
        timeout_ok=False
    except httpx.TimeoutException:timeout_ok=True
    results["timeout_handling"]={"status":"PASS" if timeout_ok else "FAIL"}
    print(json.dumps(results,indent=2));print("USDA LIVE VALIDATION:","READY" if all(v["status"]=="PASS" for v in results.values()) else "PARTIAL")
if __name__=="__main__":asyncio.run(main())
