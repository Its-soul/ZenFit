import argparse,json
from pathlib import Path

GATES=("dataset_gate","license_gate","metric_gate","calibration_gate","non_food_gate","latency_gate","regression_gate")
def main():
    p=argparse.ArgumentParser();p.add_argument("version");p.add_argument("--environment",choices=("development","production"),default="production");p.add_argument("--models-dir",type=Path,default=Path("app/zenfit_ai/models/indian_food"));args=p.parse_args();root=args.models_dir/args.version
    names=("model.pt","classes.json","config.json","metrics.json","calibration.json","dataset_manifest.json","confusion_matrix.json","reproducibility.json","model_card.md")
    missing=[name for name in names if not (root/name).exists()]
    gates={name:{"status":"BLOCKED","reason":"required evidence missing"} for name in GATES}
    if not missing:
        metrics=json.loads((root/"metrics.json").read_text());calibration=json.loads((root/"calibration.json").read_text());manifest=json.loads((root/"dataset_manifest.json").read_text())
        sources=manifest.get("sources",[manifest]);gates["dataset_gate"]={"status":"PASS","reason":"candidate artifacts complete"}
        approved=bool(sources) and all(s.get("commercial_use_allowed") is True and s.get("license_review_status")=="approved" for s in sources)
        gates["license_gate"]={"status":"PASS" if approved else "BLOCKED","reason":"all sources production-approved" if approved else "one or more source licenses are unresolved or not commercially approved"}
        gates["metric_gate"]={"status":"PASS" if metrics.get("macro_f1",0)>=.60 else "BLOCKED","reason":"macro F1 >= 0.60 required"}
        gates["calibration_gate"]={"status":"PASS" if calibration.get("ece",1)<=.15 else "BLOCKED","reason":"ECE <= 0.15 required"}
        for name in ("non_food_gate","latency_gate","regression_gate"):
            evidence=metrics.get(name);gates[name]={"status":"PASS" if evidence is True else "BLOCKED","reason":"explicit passing evidence required"}
    else:gates["dataset_gate"]["reason"]="missing: "+", ".join(missing)
    (root/"promotion_gates.json").write_text(json.dumps(gates,indent=2)) if root.exists() else None
    for name,value in gates.items():print(f"{name}: {value['status']} - {value['reason']}")
    required=GATES if args.environment=="production" else ("dataset_gate","metric_gate","calibration_gate","non_food_gate","latency_gate")
    if not all(gates[name]["status"]=="PASS" for name in required):raise SystemExit(f"{args.environment.upper()} PROMOTION BLOCKED")
    pointer="active.json" if args.environment=="production" else "development.json";(args.models_dir/pointer).write_text(json.dumps({"version":args.version},indent=2));print(f"Promoted {args.version} for {args.environment}")
if __name__=="__main__":main()
