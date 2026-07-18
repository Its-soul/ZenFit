from app.zenfit_ai.config import get_ai_settings
import importlib.util


class FoodSegAdapter:
    @property
    def adapter_path(self): return get_ai_settings().foodseg_model_dir/"zenfit_adapter.py"
    @property
    def available(self): return self.adapter_path.exists()
    def segment(self, image) -> dict:
        if not self.available:return {"available":False,"ingredients":[]}
        spec=importlib.util.spec_from_file_location("zenfit_foodseg_external",self.adapter_path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        items=module.segment(image);return {"available":True,"ingredients":[{"label":str(x["label"]),"confidence":max(0,min(1,float(x.get("confidence",0))))} for x in items or [] if x.get("label")]}
