"""Offline evaluation for a developer-supplied, license-reviewed meal image set."""
import argparse,json
from pathlib import Path
from app.ai.meal_scan.pipeline import MealScanPipeline
import asyncio

async def evaluate(root: Path):
    annotations=json.loads((root/"annotations.json").read_text())
    tp=fp=fn=top1=top3=0
    for sample in annotations:
        result=await MealScanPipeline().analyze((root/sample["image"]).read_bytes())
        expected=set(sample["expected_foods"]); predicted={food.name for food in result.foods}
        tp+=len(expected&predicted);fp+=len(predicted-expected);fn+=len(expected-predicted)
        if expected and result.foods:
            top1+=int(result.foods[0].name in expected)
            top3+=int(bool({f.name for f in result.foods[:3]}&expected))
    count=len(annotations)
    return {"samples":count,"top_1_hit_rate":top1/count if count else None,"top_3_hit_rate":top3/count if count else None,"multi_food_precision":tp/(tp+fp) if tp+fp else None,"multi_food_recall":tp/(tp+fn) if tp+fn else None}

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("root",type=Path);args=parser.parse_args()
    print(json.dumps(asyncio.run(evaluate(args.root)),indent=2))
