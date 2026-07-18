import importlib.util
from app.core.qdrant_client import qdrant_health
from app.ai.config import get_ai_settings
from app.ai.registry import registry

def main():
    s=get_ai_settings(); s.model_cache_dir.mkdir(parents=True,exist_ok=True); s.meal_upload_dir.mkdir(parents=True,exist_ok=True)
    print("ZenFit AI Setup\n")
    for module in ("sentence_transformers","xgboost","torch","PIL"):
        print(f"[{'OK' if importlib.util.find_spec(module) else 'MISSING'}] {module}")
    if importlib.util.find_spec("sentence_transformers"):
        print(f"[{'OK' if registry.get_embedding_model() else 'MISSING'}] BGE-M3")
        print(f"[{'OK' if registry.get_reranker() else 'MISSING'}] BGE Reranker")
    try: qdrant=qdrant_health()
    except Exception: qdrant=False
    print(f"[{'OK' if qdrant else 'MISSING'}] Qdrant reachable")
    for key,value in registry.status().items(): print(f"[{'OK' if value else 'MISSING'}] {key}")
if __name__=="__main__": main()
