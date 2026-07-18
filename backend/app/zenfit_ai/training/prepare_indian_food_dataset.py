import argparse,hashlib,json,random,shutil
from collections import Counter
from pathlib import Path
from PIL import Image

EXTENSIONS={".jpg",".jpeg",".png",".webp"}
def inspect(source:Path)->tuple[dict,list[Path]]:
    summary={"classes":{},"corrupt":[],"duplicates":[]};images=[];seen={}
    for cls in sorted(p for p in source.iterdir() if p.is_dir()):
        valid=0
        for path in cls.rglob("*"):
            if path.suffix.lower() not in EXTENSIONS:continue
            try:
                with Image.open(path) as image:image.verify()
                digest=hashlib.sha256(path.read_bytes()).hexdigest()
                if digest in seen:summary["duplicates"].append({"path":str(path),"same_as":str(seen[digest])});continue
                seen[digest]=path;images.append(path);valid+=1
            except Exception:summary["corrupt"].append(str(path))
        summary["classes"][cls.name]=valid
    counts=list(summary["classes"].values());summary["imbalance_ratio"]=(max(counts)/max(min(counts),1)) if counts else 0;summary["total_valid"]=len(images)
    return summary,images
def split(source:Path,destination:Path,images:list[Path],ratios=(.7,.15,.15),seed=42):
    rng=random.Random(seed)
    by_class={}
    for path in images:by_class.setdefault(path.relative_to(source).parts[0],[]).append(path)
    for cls,items in by_class.items():
        rng.shuffle(items);a=int(len(items)*ratios[0]);b=a+int(len(items)*ratios[1])
        for name,group in (("train",items[:a]),("val",items[a:b]),("test",items[b:])):
            for path in group:
                target=destination/name/cls/path.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
def main():
    p=argparse.ArgumentParser();p.add_argument("source",type=Path);p.add_argument("--output",type=Path);p.add_argument("--split",action="store_true");args=p.parse_args();summary,images=inspect(args.source)
    if args.split:
        if not args.output:raise ValueError("--output is required with --split")
        split(args.source,args.output,images)
    target=(args.output or args.source)/"dataset_summary.json";target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
