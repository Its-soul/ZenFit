DEFAULT_GRAMS = {"chapati": 40, "roti": 40, "idli": 50, "egg": 50, "banana": 118, "dosa": 100, "rice": 175, "dal": 180, "biryani": 250}


def estimate_portion(food_name: str, *, quantity: float = 1, user_grams: float | None = None, region_fraction: float | None = None, serving_size: str | None = None) -> dict:
    if user_grams is not None: return {"estimated_grams": user_grams, "confidence": 1.0, "requires_confirmation": False}
    grams = DEFAULT_GRAMS.get(food_name.lower(), 150) * quantity
    grams *= {"small":.75,"medium":1,"large":1.35}.get((serving_size or "medium").lower(),1)
    confidence = .65 if food_name.lower() in DEFAULT_GRAMS else .35
    if region_fraction: grams *= max(.5, min(2, region_fraction / .25))
    spread=.1 if confidence>=.6 else .2
    return {"estimated_grams": round(grams,1), "estimated_range_g": [round(grams*(1-spread),1),round(grams*(1+spread),1)], "confidence": confidence, "requires_confirmation": True}
