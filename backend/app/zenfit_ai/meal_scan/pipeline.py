import io,uuid
from PIL import Image
from app.zenfit_ai.meal_scan.classifier import classify
from app.zenfit_ai.meal_scan.foodsam import FoodSAMAdapter
from app.zenfit_ai.meal_scan.foodseg import FoodSegAdapter
from app.zenfit_ai.meal_scan.labels import COUNTABLE,canonical_label
from app.zenfit_ai.meal_scan.nutrition import USDANutritionClient
from app.zenfit_ai.meal_scan.portion import estimate_portion
from app.zenfit_ai.meal_scan.schemas import FoodCandidate,MealAnalysis

class MealScanPipeline:
    def __init__(self):self.foodsam,self.foodseg,self.usda=FoodSAMAdapter(),FoodSegAdapter(),USDANutritionClient()
    @staticmethod
    def decode(content:bytes):
        Image.MAX_IMAGE_PIXELS=25_000_000;probe=Image.open(io.BytesIO(content));probe.verify();image=Image.open(io.BytesIO(content));image.thumbnail((2048,2048));return image.convert("RGB")
    def _classify_regions(self,image,regions):
        evidence=[]
        if regions:
            for region in regions:
                x1,y1,x2,y2=[max(0,int(v)) for v in region["bbox"]];crop=image.crop((x1,y1,min(x2,image.width),min(y2,image.height)))
                if crop.width<8 or crop.height<8:continue
                result=classify(crop)
                if result:evidence.append(result|{"bounding_box":region["bbox"],"region_confidence":region["confidence"]})
        else:
            result=classify(image)
            if result:evidence.append(result|{"bounding_box":None,"region_confidence":.5})
        return evidence
    @staticmethod
    def _merge(evidence):
        merged={}
        for item in evidence:
            label=canonical_label(item["label"]);current=merged.setdefault(label,{"label":label,"items":[],"confidence":0,"top_candidates":[],"model_version":item.get("model_version")})
            current["items"].append(item);current["confidence"]=max(current["confidence"],item["confidence"]);current["top_candidates"]=item.get("top_candidates",[]) if item["confidence"]>=current["confidence"] else current["top_candidates"]
        return list(merged.values())
    async def analyze(self,content:bytes)->MealAnalysis:
        image=self.decode(content);sam=self.foodsam.segment(image);seg=self.foodseg.segment(image);evidence=self._classify_regions(image,sam.get("regions",[]));detections=self._merge(evidence);warnings=[]
        if not sam["available"]:warnings.append("Food region detection is unavailable; whole-meal recognition was used when possible.")
        if not seg["available"]:warnings.append("Ingredient hints are unavailable.")
        if not detections:warnings.append("Automatic food recognition is unavailable or found no confident food. Add foods manually before confirmation.")
        foods=[]
        for detection in detections:
            label=detection["label"];count=len(detection["items"]) if label in COUNTABLE and sam.get("regions") else 1;quantity_conf=.75 if count>1 else .4
            portion=estimate_portion(label,quantity=count);nutrition=await self.usda.lookup(label,portion["estimated_grams"]) or {};food_conf=detection["confidence"];level="high" if food_conf>=.8 else "medium" if food_conf>=.55 else "low"
            foods.append(FoodCandidate(name=label,quantity=count,estimated_grams=portion["estimated_grams"],confidence=food_conf,nutrition=nutrition,usda_food_id=nutrition.get("usda_food_id"),matched_description=nutrition.get("matched_description"),food_confidence=food_conf,quantity_confidence=quantity_conf,portion_confidence=portion["confidence"],nutrition_match_confidence=nutrition.get("match_confidence",0),confidence_level=level,top_candidates=detection["top_candidates"],bounding_box=detection["items"][0].get("bounding_box"),model_version=detection.get("model_version")))
        totals={key:round(sum(f.nutrition.get(key,0) for f in foods),1) for key in ("calories","protein_g","carbs_g","fat_g","fiber_g")}
        return MealAnalysis(analysis_id=str(uuid.uuid4()),foods=foods,nutrition=totals,warnings=warnings)
