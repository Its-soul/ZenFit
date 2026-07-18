import asyncio
from app.zenfit_ai.meal_scan.portion import estimate_portion
from app.zenfit_ai.meal_scan.foodsam import FoodSAMAdapter
from app.zenfit_ai.meal_scan.foodseg import FoodSegAdapter
from app.zenfit_ai.meal_scan.nutrition import USDANutritionClient
from app.zenfit_ai.meal_scan.storage import MealAnalysisStore

def test_user_correction_changes_portion(): assert estimate_portion("chapati",quantity=3)["estimated_grams"]==120
def test_optional_segmentation_does_not_crash():
    assert "available" in FoodSAMAdapter().segment(None); assert "available" in FoodSegAdapter().segment(None)
def test_usda_unconfigured(monkeypatch):
    monkeypatch.setattr("app.zenfit_ai.meal_scan.nutrition.get_ai_settings",lambda:type("S",(),{"usda_api_key":None})())
    assert asyncio.run(USDANutritionClient().lookup("unknown food",100)) is None
def test_local_reference_recalculates_correction(monkeypatch):
    monkeypatch.setattr("app.zenfit_ai.meal_scan.nutrition.get_ai_settings",lambda:type("S",(),{"usda_api_key":None})())
    one=asyncio.run(USDANutritionClient().lookup("chapati",40));three=asyncio.run(USDANutritionClient().lookup("chapati",120))
    assert three["calories"]==one["calories"]*3 and three["requires_confirmation"]
def test_analysis_store_enforces_owner():
    class Redis:
        value=None
        def setex(self,key,ttl,value):self.value=value
        def get(self,key):return self.value
        def delete(self,key):pass
    store=MealAnalysisStore();store_client=Redis()
    import app.zenfit_ai.meal_scan.storage as module
    original=module.get_redis_client;module.get_redis_client=lambda:store_client
    try:
        store.save(user_id="a",analysis={"analysis_id":"id"});assert store.get_for_user(user_id="a",analysis_id="id");assert store.get_for_user(user_id="b",analysis_id="id") is None
    finally:module.get_redis_client=original
