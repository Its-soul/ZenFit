"""Evaluate stored prediction evidence. This module never imports or loads a model."""
import argparse
import json
from pathlib import Path

from app.ai.meal_scan.open_set import OpenSetThresholds
from training.open_set_evaluation import evaluate_rows, threshold_sweep


def main():
    parser=argparse.ArgumentParser();parser.add_argument("evidence",type=Path);parser.add_argument("--thresholds",type=Path,required=True);parser.add_argument("--output",type=Path,default=Path("open_set_evaluation.json"));args=parser.parse_args()
    payload=json.loads(args.evidence.read_text(encoding="utf-8"));rows=payload.get("predictions",payload)
    thresholds=OpenSetThresholds.from_json(args.thresholds);result=evaluate_rows(rows,thresholds);result["threshold_sweep"]=threshold_sweep(rows,thresholds.model_version)
    args.output.write_text(json.dumps(result,indent=2),encoding="utf-8");print(f"Wrote open-set evaluation to {args.output}")


if __name__=="__main__":main()
