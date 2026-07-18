"""Analyze stored JSON evidence without loading classifier weights."""
import argparse
import json
from pathlib import Path

from training.open_set_evaluation import threshold_sweep


def recommend(results: list[dict]) -> dict:
    def score(item):
        metrics=item["metrics"]
        return (metrics["overall_open_set_accuracy"] or 0) - (metrics["unknown_food"]["false_acceptance_rate"] or 0) - (metrics["non_food"]["false_food_acceptance_rate"] or 0)
    best=max(results,key=score)
    return {"status":"candidate","selection":"synthetic/offline evidence objective; requires reviewed online validation","thresholds":best["thresholds"],"metrics":best["metrics"]}


def main():
    parser=argparse.ArgumentParser();parser.add_argument("evidence",type=Path);parser.add_argument("--model-version",required=True);parser.add_argument("--output",type=Path,default=Path("recommended_thresholds.json"));args=parser.parse_args()
    payload=json.loads(args.evidence.read_text(encoding="utf-8"));rows=payload.get("predictions",payload);result=recommend(threshold_sweep(rows,args.model_version));args.output.write_text(json.dumps(result,indent=2),encoding="utf-8");print(f"Wrote candidate thresholds to {args.output}")


if __name__=="__main__":main()
