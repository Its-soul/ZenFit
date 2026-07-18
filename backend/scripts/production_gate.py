import json
from pathlib import Path
from app.ai.registry import registry

def main():
    root=Path("../data/models/indian_food");active=root/"active.json";dev=root/"development.json"
    core=all(registry.status()[k] for k in ("bge_embeddings","bge_reranker"))
    development=dev.exists() or active.exists();production=False;reasons=[]
    if active.exists():
        version=json.loads(active.read_text())["version"];gate=root/version/"promotion_gates.json"
        if gate.exists():
            gates=json.loads(gate.read_text());production=all(v.get("status")=="PASS" for v in gates.values())
            reasons=[f"{k}: {v.get('reason','failed')}" for k,v in gates.items() if v.get("status")!="PASS"]
        else:reasons=["active candidate has no promotion-gate evidence"]
    else:reasons=["no production-active classifier"]
    print(f"CORE ZENFIT AI:\n{'READY' if core else 'BLOCKED'}\n\nDEVELOPMENT MEAL RECOGNITION:\n{'READY' if development else 'BLOCKED'}\n\nPRODUCTION MEAL RECOGNITION:\n{'READY' if production else 'BLOCKED'}")
    if reasons:print("\nReason:\n"+"\n".join(reasons))
if __name__=="__main__":main()
