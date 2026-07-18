"""Prepare conservative canonical classes from the CC0 recipe-image dataset."""
import argparse,hashlib,json,os,random,re,shutil
from collections import Counter,defaultdict
from pathlib import Path
import pandas as pd
from PIL import Image

PATTERNS=[
 ("palak_paneer",r"\b(palak|spinach) paneer\b"),("jeera_rice",r"\b(jeera|cumin) (rice|pulao|pulav|pilaf)\b"),("biryani",r"\bbiryani\b"),
 ("rajma",r"\b(rajma|kidney bean curry)\b"),("chole",r"\b(chole|chana masala)\b"),("poha",r"\bpoha\b"),("upma",r"\bupma\b"),
 ("idli",r"\bidli\b"),("dosa",r"\bdosa\b"),("sambar",r"\b(sambar|sambhar)\b"),("omelette",r"\b(omelette|omelet)\b"),
 ("boiled_egg",r"\b(boiled egg|egg boil)\b"),("fried_egg",r"\bfried egg\b"),("curd",r"\b(curd|yogurt|yoghurt|raita)\b"),
 ("salad",r"\bsalad\b"),("paratha",r"\b(paratha|parantha|parotta)\b"),("chapati",r"\b(chapati|phulka|roti)\b"),
 ("khichdi",r"\b(khichdi|khichadi|pongal)\b"),("grilled_chicken",r"\b(grilled|tandoori) chicken\b"),
 ("chicken_curry",r"\b(chicken curry|murgh curry|chicken masala)\b"),("fish_curry",r"\b(fish curry|meen curry|machher jhol|fish kuzhambu)\b"),
 ("dal",r"\b(dal|dahl|lentil curry)\b"),("paneer_curry",r"\b(paneer curry|paneer masala|kadai paneer|shahi paneer|matar paneer)\b"),
]
def label(name):
    normalized=re.sub(r"[_()-]+"," ",name.lower())
    if "dalna" in normalized:return None
    return next((canonical for canonical,pattern in PATTERNS if re.search(pattern,normalized)),None)
def main():
    p=argparse.ArgumentParser();p.add_argument("--raw",type=Path,default=Path("/data/raw/kaggle/5000_indian_cuisines"));p.add_argument("--output",type=Path,default=Path("/data/training/indian_food"));p.add_argument("--min-images",type=int,default=15);p.add_argument("--seed",type=int,default=42);args=p.parse_args()
    if args.output.exists() and any(args.output.iterdir()):raise FileExistsError("Prepared output exists; remove it explicitly to regenerate")
    rows=pd.read_csv(args.raw/"cuisine_updated.csv");images=args.raw/"data"/"data";indexed={int(m.group(1)):p for p in images.iterdir() if (m:=re.match(r"(\d+)\.",p.name))};seen_sha=set();seen_visual=set();items=defaultdict(list);excluded=Counter()
    for index,row in rows.iterrows():
        path=indexed.get(index+1);canonical=label(str(row["name"]))
        if not path or not canonical:excluded["no_image_or_supported_label"]+=1;continue
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        with Image.open(path) as im:visual=''.join('1' if x>=128 else '0' for x in im.convert('L').resize((8,8)).getdata())
        if digest in seen_sha or visual in seen_visual:excluded["duplicate"]+=1;continue
        seen_sha.add(digest);seen_visual.add(visual);items[canonical].append({"path":path,"source_row":index,"recipe_name":row["name"],"sha256":digest})
    included={k:v for k,v in items.items() if len(v)>=args.min_images};rng=random.Random(args.seed);manifest={"dataset_version":"kaggle-5000-indian-cuisines-v1-2026-07","random_seed":args.seed,"ratios":{"train":.7,"val":.15,"test":.15},"sources":[json.loads((args.raw/"dataset_manifest.json").read_text())],"classes":{},"files":[],"excluded":dict(excluded)}
    for canonical,records in sorted(included.items()):
        rng.shuffle(records);n=len(records);a=int(n*.7);b=a+int(n*.15);parts={"train":records[:a],"val":records[a:b],"test":records[b:]};manifest["classes"][canonical]={k:len(v) for k,v in parts.items()}|{"total":n,"status":"READY" if n>=30 else "LOW_DATA"}
        for split,group in parts.items():
            for i,record in enumerate(group):
                suffix=record["path"].suffix.lower();target=args.output/split/canonical/f"{record['sha256'][:16]}{suffix}";target.parent.mkdir(parents=True,exist_ok=True)
                try:os.link(record["path"],target)
                except OSError:shutil.copy2(record["path"],target)
                manifest["files"].append({"path":str(target.relative_to(args.output)),"source_dataset":"campusx/5000-indian-cuisines-datasetwith-images","source_row":record["source_row"],"recipe_name":record["recipe_name"],"sha256":record["sha256"]})
    manifest["excluded_classes"]={k:len(v) for k,v in items.items() if k not in included};args.output.mkdir(parents=True,exist_ok=True);(args.output/"split_manifest.json").write_text(json.dumps(manifest,indent=2));print(json.dumps({"classes":manifest["classes"],"excluded_classes":manifest["excluded_classes"],"prepared_images":len(manifest["files"])},indent=2))
if __name__=="__main__":main()
