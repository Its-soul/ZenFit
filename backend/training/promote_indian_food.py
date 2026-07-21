import argparse,json
from pathlib import Path

GATES=("dataset_gate","license_gate","metric_gate","calibration_gate","latency_gate","regression_gate","unknown_food_gate","non_food_gate","open_set_evidence_size_gate")
DEFAULT_GATE_CONFIG=Path(__file__).parent/"configs"/"open_set_release_gates.json"

def evaluate_developer_beta_gates(root:Path):
    release=root/"release_evidence.json"
    if not release.is_file():return {"release_evidence":{"status":"BLOCKED","reason":"release_evidence.json is missing"}}
    payload=json.loads(release.read_text());checks=payload.get("developer_beta",{}).get("checks",{})
    return {name:{"status":"PASS" if passed else "BLOCKED","reason":"developer-beta criterion satisfied" if passed else "developer-beta criterion not satisfied"} for name,passed in checks.items()}

def evaluate_gates(root:Path, gate_config:Path=DEFAULT_GATE_CONFIG):
    names=("model.pt","classes.json","config.json","metrics.json","calibration.json","dataset_manifest.json","confusion_matrix.json","reproducibility.json","model_card.md","open_set_thresholds.json","release_evidence.json")
    missing=[name for name in names if not (root/name).exists()]
    gates={name:{"status":"BLOCKED","reason":"required evidence missing"} for name in GATES}
    if missing:gates["dataset_gate"]["reason"]="missing: "+", ".join(missing);return gates
    metrics=json.loads((root/"metrics.json").read_text());calibration=json.loads((root/"calibration.json").read_text());manifest=json.loads((root/"dataset_manifest.json").read_text());evidence=json.loads((root/"release_evidence.json").read_text());requirements=json.loads(gate_config.read_text())
    sources=manifest.get("sources",[manifest]);gates["dataset_gate"]={"status":"PASS","reason":"candidate artifacts complete"}
    evidence_license=evidence.get("open_set_evidence_license") or {};approved=bool(sources) and all(s.get("commercial_use_allowed") is True and str(s.get("license_review_status","")).lower()=="approved" for s in sources) and evidence_license.get("research_only_samples",1)==0
    gates["license_gate"]={"status":"PASS" if approved else "BLOCKED","reason":"all sources production-approved" if approved else "one or more source licenses are unresolved or not commercially approved"}
    gates["metric_gate"]={"status":"PASS" if metrics.get("macro_f1",0)>=.60 else "BLOCKED","reason":"macro F1 >= 0.60 required"}
    gates["calibration_gate"]={"status":"PASS" if calibration.get("ece",1)<=.15 else "BLOCKED","reason":"ECE <= 0.15 required"}
    for name in ("latency_gate","regression_gate"):
        passed=metrics.get(name) is True;gates[name]={"status":"PASS" if passed else "BLOCKED","reason":"explicit passing evidence required"}
    unknown=evidence.get("unknown_food",{});nonfood=evidence.get("non_food",{});supported=evidence.get("supported_food",{})
    unknown_rate=unknown.get("rejection_rate",0);nonfood_rate=nonfood.get("rejection_rate",0)
    gates["unknown_food_gate"]={"status":"PASS" if unknown_rate>=requirements["minimum_unknown_food_rejection_rate"] else "BLOCKED","reason":f"rejection rate {unknown_rate:.3f}; requires {requirements['minimum_unknown_food_rejection_rate']:.3f}"}
    gates["non_food_gate"]={"status":"PASS" if nonfood_rate>=requirements["minimum_non_food_rejection_rate"] else "BLOCKED","reason":f"rejection rate {nonfood_rate:.3f}; requires {requirements['minimum_non_food_rejection_rate']:.3f}"}
    unknown_classes=unknown.get("class_count",len({item.get("source_class") for item in unknown.get("results",[]) if item.get("source_class")}));nonfood_categories=nonfood.get("category_count",len({item.get("category",item.get("probe")) for item in nonfood.get("results",[]) if item.get("category",item.get("probe"))}))
    checks={"supported_food_samples":supported.get("sample_count",evidence.get("validation_samples",0))>=requirements["minimum_supported_food_samples"],"unknown_food_classes":unknown_classes>=requirements["minimum_unknown_food_classes"],"unknown_food_images":unknown.get("sample_count",0)>=requirements["minimum_unknown_food_images"],"non_food_categories":nonfood_categories>=requirements["minimum_non_food_categories"],"non_food_images":nonfood.get("sample_count",0)>=requirements["minimum_non_food_images"]}
    gates["open_set_evidence_size_gate"]={"status":"PASS" if all(checks.values()) else "BLOCKED","reason":"project evidence minimums satisfied" if all(checks.values()) else "insufficient evidence: "+", ".join(name for name,passed in checks.items() if not passed)}
    return gates

def main():
    p=argparse.ArgumentParser();p.add_argument("version");p.add_argument("--environment",choices=("developer-beta","development","production"),default="production");p.add_argument("--models-dir",type=Path,default=Path("../data/models/indian_food"));p.add_argument("--gate-config",type=Path,default=DEFAULT_GATE_CONFIG);args=p.parse_args();root=args.models_dir/args.version
    gates=evaluate_gates(root,args.gate_config) if args.environment=="production" else evaluate_developer_beta_gates(root)
    (root/"promotion_gates.json").write_text(json.dumps(gates,indent=2)) if root.exists() else None
    for name,value in gates.items():print(f"{name}: {value['status']} - {value['reason']}")
    if not gates or not all(value["status"]=="PASS" for value in gates.values()):raise SystemExit(f"{args.environment.upper()} PROMOTION BLOCKED")
    pointer="active.json" if args.environment=="production" else "developer_beta.json"
    metadata={"version":args.version,"status":"PRODUCTION_APPROVED" if args.environment=="production" else "DEVELOPER_BETA","manual_correction_required":args.environment!="production","confidence_required":True,"top_k_required":True}
    (args.models_dir/pointer).write_text(json.dumps(metadata,indent=2));print(f"Promoted {args.version} for {args.environment}")
if __name__=="__main__":main()
