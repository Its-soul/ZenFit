import json,math
from pathlib import Path
from app.zenfit_ai.config import get_ai_settings

def _active_artifacts(settings):
    model_root=settings.indian_food_model_path.parent/"indian_food";active=model_root/"active.json"
    if settings.app_env != "production" and (model_root/"development.json").exists():active=model_root/"development.json"
    if active.exists():
        manifest=json.loads(active.read_text());root=active.parent/manifest["version"]
        weights=root/"model.pt" if (root/"model.pt").exists() else root/"indian_food.pt";classes=root/"classes.json" if (root/"classes.json").exists() else root/"indian_food_classes.json";metadata=root/"config.json" if (root/"config.json").exists() else root/"indian_food_model.json"
        return weights,classes,metadata
    return settings.indian_food_model_path,settings.indian_food_classes_path,settings.indian_food_model_path.with_name("indian_food_model.json")

def load_classifier():
    settings=get_ai_settings();weights,classes_path,metadata_path=_active_artifacts(settings)
    if not weights.exists() or not classes_path.exists():raise FileNotFoundError("No promoted Indian-food classifier is installed")
    import torch
    from torchvision.models import efficientnet_b0
    classes=json.loads(classes_path.read_text());model=efficientnet_b0(num_classes=len(classes));model.load_state_dict(torch.load(weights,map_location="cpu",weights_only=True));model.eval()
    metadata=json.loads(metadata_path.read_text()) if metadata_path.exists() else {"version":"legacy","architecture":"efficientnet_b0"}
    return {"model":model,"classes":classes,"metadata":metadata}

def classify(image,top_k:int=3)->dict|None:
    from app.zenfit_ai.registry import registry
    loaded=registry.get_food_classifier()
    if loaded is None:return None
    import torch
    from torchvision.transforms import v2
    tensor=v2.Compose([v2.ToImage(),v2.Resize((224,224)),v2.ToDtype(torch.float32,scale=True),v2.Normalize([.485,.456,.406],[.229,.224,.225])])(image).unsqueeze(0)
    with torch.inference_mode():probabilities=loaded["model"](tensor).softmax(1)[0]
    values,indices=probabilities.topk(min(top_k,len(loaded["classes"])))
    candidates=[{"label":loaded["classes"][int(i)],"confidence":round(float(v),4)} for v,i in zip(values,indices)]
    confidence=candidates[0]["confidence"];settings=get_ai_settings();margin=confidence-(candidates[1]["confidence"] if len(candidates)>1 else 0);entropy=-sum(c["confidence"]*math.log(max(c["confidence"],1e-12)) for c in candidates)
    level="high" if confidence>=settings.meal_classifier_high_confidence else "medium" if confidence>=settings.meal_classifier_min_confidence else "low"
    detected=confidence>=settings.meal_classifier_min_confidence and margin>=.10
    return {"food_detected":detected,"reason":None if detected else "low_food_confidence","label":candidates[0]["label"] if detected else "unknown_food","confidence":confidence,"confidence_level":level,"top_1_top_2_margin":round(margin,4),"prediction_entropy":round(entropy,4),"top_candidates":candidates,"model_version":loaded["metadata"].get("version","unknown")}
