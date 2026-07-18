from app.zenfit_ai.config import get_ai_settings
import importlib.util


class FoodSAMAdapter:
    @property
    def adapter_path(self): return get_ai_settings().foodsam_model_dir/"zenfit_adapter.py"
    @property
    def available(self): return self.adapter_path.exists()
    def segment(self, image) -> dict:
        if not self.available: return {"available": False, "regions": []}
        spec=importlib.util.spec_from_file_location("zenfit_foodsam_external",self.adapter_path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        raw=module.segment(image);regions=[]
        for index,item in enumerate(raw or []):
            bbox=item.get("bbox") or item.get("bounding_box")
            if bbox and len(bbox)==4:regions.append({"region_id":item.get("region_id",index+1),"bbox":[float(x) for x in bbox],"confidence":max(0,min(1,float(item.get("confidence",0)))),"mask":None})
        return {"available": True, "regions": regions}
