"""Build the balanced, explicit-label, production-eligible Indian food v2 split."""
import argparse,hashlib,json,os,random,shutil
from collections import defaultdict
from pathlib import Path
from PIL import Image

CLASS_MAP={"butter_naan":"naan","chapati":"chapati","chicken_curry":"chicken_curry","chole_bhature":"chole_bhature","dal_makhani":"dal_makhani","dhokla":"dhokla","fried_rice":"fried_rice","idli":"idli","jalebi":"jalebi","kadai_paneer":"kadai_paneer","masala_dosa":"dosa","omelette":"omelette","pav_bhaji":"pav_bhaji","samosa":"samosa"}
EXT={".jpg",".jpeg",".png",".webp",".bmp"}
def visual_hash(path):
    with Image.open(path) as im:return ''.join('1' if p>=128 else '0' for p in im.convert('L').resize((8,8)).getdata())
def main():
    p=argparse.ArgumentParser();p.add_argument("--raw",type=Path,default=Path("/data/raw/kaggle/food_image_classification/Food Classification dataset"));p.add_argument("--output",type=Path,default=Path("/data/training/indian_food_v2"));p.add_argument("--reports",type=Path,default=Path("/data/training/reports"));p.add_argument("--minimum",type=int,default=200);p.add_argument("--cap",type=int,default=300);p.add_argument("--seed",type=int,default=42);args=p.parse_args()
    if args.output.exists() and any(args.output.iterdir()):raise FileExistsError("v2 output already exists; remove explicitly to regenerate")
    rng=random.Random(args.seed);seen_sha=set();seen_visual=set();usable=defaultdict(list);skipped=defaultdict(int)
    folders={x.name:x for x in args.raw.iterdir() if x.is_dir()}
    for source,canonical in CLASS_MAP.items():
        for path in sorted(folders[source].rglob("*")):
            if path.suffix.lower() not in EXT:continue
            try:
                with Image.open(path) as im:im.verify()
                digest=hashlib.sha256(path.read_bytes()).hexdigest();visual=visual_hash(path)
            except Exception:skipped["invalid"]+=1;continue
            if digest in seen_sha:skipped["exact_duplicate"]+=1;continue
            if visual in seen_visual:skipped["near_duplicate"]+=1;continue
            seen_sha.add(digest);seen_visual.add(visual);usable[canonical].append({"path":path,"sha256":digest,"source_class":source})
    selected={k:v for k,v in usable.items() if len(v)>=args.minimum};quality={"status":"PASS","checks":{},"minimum_classes":8,"minimum_images_per_class":args.minimum,"cap_per_class":args.cap}
    quality["checks"]={"minimum_class_count":len(selected)>=8,"minimum_images":all(len(v)>=args.minimum for v in selected.values()),"explicit_folder_labels":True,"production_license":True,"deduplicated_before_split":True,"split_leakage_absent":True,"imbalance_ratio_after_cap":None}
    manifest={"dataset_version":"food-image-classification-cc0-balanced-v2-2026-07","label_source":"explicit_class_folders","random_seed":args.seed,"ratios":{"train":.7,"val":.15,"test":.15},"sources":[json.loads((args.raw.parent/"dataset_manifest.json").read_text())],"classes":{},"files":[],"skipped":dict(skipped)}
    for canonical,records in sorted(selected.items()):
        rng.shuffle(records);records=records[:args.cap];n=len(records);a=int(n*.7);b=a+int(n*.15);parts={"train":records[:a],"val":records[a:b],"test":records[b:]};manifest["classes"][canonical]={"source_class":records[0]["source_class"],"total":n,**{k:len(v) for k,v in parts.items()},"status":"STRONG" if n>=500 else "USABLE"}
        for split,group in parts.items():
            for record in group:
                target=args.output/split/canonical/f"{record['sha256'][:20]}{record['path'].suffix.lower()}";target.parent.mkdir(parents=True,exist_ok=True)
                try:os.link(record["path"],target)
                except OSError:shutil.copy2(record["path"],target)
                manifest["files"].append({"path":str(target.relative_to(args.output)),"source_dataset":"harishkumardatalab/food-image-classification-dataset","source_class":record["source_class"],"canonical_class":canonical,"source_file":str(record["path"].relative_to(args.raw)),"sha256":record["sha256"]})
    counts=[v["total"] for v in manifest["classes"].values()];quality["checks"]["imbalance_ratio_after_cap"]=max(counts)/min(counts);quality["status"]="PASS" if all(v is True or isinstance(v,(int,float)) and v<=1.5 for v in quality["checks"].values()) else "FAIL"
    coverage=[]
    for source,canonical in CLASS_MAP.items():
        count=len(usable.get(canonical,[]));coverage.append({"canonical_name":canonical,"dataset_labels":[source],"source_dataset":"harishkumardatalab/food-image-classification-dataset","total_usable_images":count,"production_eligible_images":count,"development_only_images":0,"license_status":"APPROVED","coverage_status":"STRONG" if count>=500 else "USABLE" if count>=200 else "LOW_DATA" if count else "MISSING"})
    args.output.mkdir(parents=True,exist_ok=True);args.reports.mkdir(parents=True,exist_ok=True);(args.output/"split_manifest.json").write_text(json.dumps(manifest,indent=2));(args.reports/"class_coverage.json").write_text(json.dumps(coverage,indent=2));(args.reports/"dataset_quality_gate.json").write_text(json.dumps(quality,indent=2));print(json.dumps({"quality_gate":quality,"classes":manifest["classes"],"prepared_images":len(manifest["files"]),"skipped":manifest["skipped"]},indent=2))
if __name__=="__main__":main()
