import argparse,json
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument("versions",nargs="*",default=["1.0.0","0.2.0","1.1.0"]);p.add_argument("--models-dir",type=Path,default=Path("app/zenfit_ai/models/indian_food"));args=p.parse_args();rows=[]
    for version in args.versions:
        root=args.models_dir/version
        if not (root/"metrics.json").exists():continue
        m=json.loads((root/"metrics.json").read_text());c=json.loads((root/"config.json").read_text());cal=json.loads((root/"calibration.json").read_text());manifest=json.loads((root/"dataset_manifest.json").read_text());sources=manifest.get("sources",[]);license_gate=bool(sources) and all(s.get("commercial_use_allowed") is True and s.get("license_review_status")=="approved" for s in sources)
        rows.append({"version":version,"dataset":c.get("dataset_version"),"classes":c.get("class_count"),"training_images":c.get("training_images"),"accuracy":m.get("accuracy"),"balanced_accuracy":m.get("balanced_accuracy"),"macro_f1":m.get("macro_f1"),"weighted_f1":m.get("weighted_f1"),"top_3_accuracy":m.get("top_3_accuracy"),"brier_score":cal.get("brier_score"),"ece":cal.get("ece"),"license_gate":"PASS" if license_gate else "BLOCKED","metric_gate":"PASS" if m.get("macro_f1",0)>=.6 else "BLOCKED","class_set_comparison_caveat":True})
    print(json.dumps(rows,indent=2))
if __name__=="__main__":main()
