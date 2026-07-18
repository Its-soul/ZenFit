import io,uuid
from PIL import Image
from app.ai.meal_scan.classifier import classify
from app.ai.meal_scan.foodsam import FoodSAMAdapter
from app.ai.meal_scan.foodseg import FoodSegAdapter
from app.ai.meal_scan.labels import COUNTABLE,canonical_label
from app.ai.meal_scan.nutrition import USDANutritionClient
from app.ai.meal_scan.portion import estimate_portion
from app.ai.meal_scan.schemas import FoodCandidate,MealAnalysis
from app.ai.config import get_ai_settings
from app.ai.meal_scan.food_detector import UnavailableFoodDetector
from app.ai.meal_scan.open_set import Candidate, OpenSetDecision, OpenSetDecisionEngine, OpenSetInput, OpenSetThresholds

MESSAGES = {
    OpenSetDecision.SUPPORTED_FOOD: "Food recognized. Review the result before saving.",
    OpenSetDecision.UNKNOWN_FOOD: "We found food in your image, but ZenFit cannot identify it reliably yet. Please select or enter the food manually.",
    OpenSetDecision.NON_FOOD: "This does not appear to be a meal image. Please upload a food photo or log your meal manually.",
    OpenSetDecision.LOW_CONFIDENCE: "We're not fully sure about this food. Review the possible matches or enter it manually.",
    OpenSetDecision.MODEL_UNAVAILABLE: "AI meal recognition is currently unavailable. You can still log your meal manually.",
}

def _release_thresholds(model_version:str|None)->OpenSetThresholds:
    settings=get_ai_settings()
    path=settings.indian_food_model_path.parent/"indian_food"/(model_version or "")/"open_set_thresholds.json"
    if path.is_file():
        configured=OpenSetThresholds.from_json(path)
        if settings.app_env=="production" and configured.status!="approved":
            raise RuntimeError("production open-set thresholds are not approved")
        return configured
    return OpenSetThresholds(model_version=model_version or "unavailable")

class MealScanPipeline:
    def __init__(self, food_detector=None, thresholds=None):
        self.foodsam,self.foodseg,self.usda=FoodSAMAdapter(),FoodSegAdapter(),USDANutritionClient()
        self.food_detector = food_detector or UnavailableFoodDetector()
        self.thresholds = thresholds
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
        image=self.decode(content)
        if not get_ai_settings().heavy_models_enabled:
            return MealAnalysis(analysis_id=str(uuid.uuid4()),foods=[],nutrition={key:0.0 for key in ("calories","protein_g","carbs_g","fat_g","fiber_g")},warnings=[MESSAGES[OpenSetDecision.MODEL_UNAVAILABLE]],recognition_decision=OpenSetDecision.MODEL_UNAVAILABLE,recognition_message=MESSAGES[OpenSetDecision.MODEL_UNAVAILABLE],recognition_reason_codes=["heavy_models_disabled"])
        sam=self.foodsam.segment(image);seg=self.foodseg.segment(image);evidence=self._classify_regions(image,sam.get("regions",[]));warnings=[]
        detector_result=self.food_detector.predict(image) if self.food_detector.is_available() else None
        best=max(evidence,key=lambda item:item.get("top1_confidence",0),default=None)
        version=best.get("model_version") if best else None
        thresholds=self.thresholds or _release_thresholds(version)
        decision=OpenSetDecisionEngine(thresholds).decide(OpenSetInput(top_candidates=tuple(Candidate(item["label"],item["confidence"]) for item in (best or {}).get("top_candidates",[])),entropy=(best or {}).get("entropy"),food_probability=detector_result.food_probability if detector_result else None,model_version=version,model_available=best is not None))
        accepted=evidence if decision.decision is OpenSetDecision.SUPPORTED_FOOD else []
        detections=self._merge([item|{"label":item["top_candidates"][0]["label"],"confidence":item["top1_confidence"]} for item in accepted]);warnings=[]
        if not sam["available"]:warnings.append("Food region detection is unavailable; whole-meal recognition was used when possible.")
        if not seg["available"]:warnings.append("Ingredient hints are unavailable.")
        if not detections:warnings.append(MESSAGES[decision.decision])
        foods=[]
        for detection in detections:
            label=detection["label"];count=len(detection["items"]) if label in COUNTABLE and sam.get("regions") else 1;quantity_conf=.75 if count>1 else .4
            portion=estimate_portion(label,quantity=count);nutrition=await self.usda.lookup(label,portion["estimated_grams"]) or {};food_conf=detection["confidence"];level="high" if food_conf>=.8 else "medium" if food_conf>=.55 else "low"
            foods.append(FoodCandidate(name=label,quantity=count,estimated_grams=portion["estimated_grams"],confidence=food_conf,nutrition=nutrition,usda_food_id=nutrition.get("usda_food_id"),matched_description=nutrition.get("matched_description"),food_confidence=food_conf,quantity_confidence=quantity_conf,portion_confidence=portion["confidence"],nutrition_match_confidence=nutrition.get("match_confidence",0),confidence_level=level,top_candidates=detection["top_candidates"],bounding_box=detection["items"][0].get("bounding_box"),model_version=detection.get("model_version")))
        totals={key:round(sum(f.nutrition.get(key,0) for f in foods),1) for key in ("calories","protein_g","carbs_g","fat_g","fiber_g")}
        return MealAnalysis(analysis_id=str(uuid.uuid4()),foods=foods,nutrition=totals,warnings=warnings,recognition_decision=decision.decision,recognition_message=MESSAGES[decision.decision],recognition_reason_codes=list(decision.reason_codes),top_candidates=[{"label":item.label,"confidence":item.confidence} for item in decision.top_candidates])
