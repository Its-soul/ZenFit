# Small USDA-derived per-100g development fallback; not a substitute for FoodData Central matching.
VALUES={
 "chapati":{"calories":297,"protein_g":9.6,"carbs_g":46,"fat_g":7.5,"fiber_g":6.7},
 "roti":{"calories":297,"protein_g":9.6,"carbs_g":46,"fat_g":7.5,"fiber_g":6.7},
 "rice":{"calories":130,"protein_g":2.7,"carbs_g":28.2,"fat_g":.3,"fiber_g":.4},
 "dal":{"calories":116,"protein_g":9,"carbs_g":20.1,"fat_g":.4,"fiber_g":7.9},
 "egg":{"calories":143,"protein_g":12.6,"carbs_g":.7,"fat_g":9.5,"fiber_g":0},
 "banana":{"calories":89,"protein_g":1.1,"carbs_g":22.8,"fat_g":.3,"fiber_g":2.6},
 "idli":{"calories":128,"protein_g":4.2,"carbs_g":25,"fat_g":.7,"fiber_g":1.5},
 "dosa":{"calories":168,"protein_g":3.9,"carbs_g":28,"fat_g":4.2,"fiber_g":1.2},
 "paneer":{"calories":321,"protein_g":21.4,"carbs_g":3.6,"fat_g":25,"fiber_g":0},
}
REFERENCES={
 "chapati":{"serving_description":"1 medium","serving_grams":40,"source":"USDA FoodData Central generic whole-wheat flatbread reference","source_url":"https://fdc.nal.usda.gov/fdc-app.html#/food-search?query=chapati","reference_estimate":True},
 "roti":{"serving_description":"1 medium","serving_grams":40,"source":"USDA FoodData Central generic whole-wheat flatbread reference","source_url":"https://fdc.nal.usda.gov/fdc-app.html#/food-search?query=roti","reference_estimate":True},
 "rice":{"serving_description":"1 cup cooked","serving_grams":175,"source":"USDA FoodData Central cooked white rice reference","source_url":"https://fdc.nal.usda.gov/fdc-app.html#/food-search?query=cooked%20white%20rice","reference_estimate":False},
 "dal":{"serving_description":"1 bowl","serving_grams":180,"source":"USDA FoodData Central cooked lentils reference","source_url":"https://fdc.nal.usda.gov/fdc-app.html#/food-search?query=cooked%20lentils","reference_estimate":True},
 "egg":{"serving_description":"1 large","serving_grams":50,"source":"USDA FoodData Central whole egg reference","source_url":"https://fdc.nal.usda.gov/fdc-app.html#/food-search?query=whole%20egg","reference_estimate":False},
 "banana":{"serving_description":"1 medium","serving_grams":118,"source":"USDA FoodData Central banana reference","source_url":"https://fdc.nal.usda.gov/fdc-app.html#/food-search?query=banana","reference_estimate":False},
 "idli":{"serving_description":"1 piece","serving_grams":50,"source":"USDA FoodData Central idli search reference","source_url":"https://fdc.nal.usda.gov/fdc-app.html#/food-search?query=idli","reference_estimate":True},
 "dosa":{"serving_description":"1 plain dosa","serving_grams":100,"source":"USDA FoodData Central dosa search reference","source_url":"https://fdc.nal.usda.gov/fdc-app.html#/food-search?query=dosa","reference_estimate":True},
 "paneer":{"serving_description":"100 g","serving_grams":100,"source":"USDA FoodData Central paneer search reference","source_url":"https://fdc.nal.usda.gov/fdc-app.html#/food-search?query=paneer","reference_estimate":True}
}
def local_lookup(name:str,grams:float):
    key=" ".join(name.lower().replace("_"," ").split());key={"plain rice":"rice","boiled egg":"egg","fried egg":"egg"}.get(key,key);row=VALUES.get(key)
    if not row:return None
    factor=grams/100
    reference=REFERENCES[key]
    return {k:round(v*factor,1) for k,v in row.items()}|{"usda_food_id":None,"matched_description":reference["source"],"match_confidence":.7 if not reference["reference_estimate"] else .55,"requires_confirmation":True,"source":"local_reference","source_url":reference["source_url"],"serving_description":reference["serving_description"],"serving_grams":reference["serving_grams"],"reference_estimate":reference["reference_estimate"]}
