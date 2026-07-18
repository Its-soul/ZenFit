"""Read-only image/metadata audits for raw Kaggle datasets."""
import argparse,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
from PIL import Image

EXT={".jpg",".jpeg",".png",".webp",".bmp"}
def ahash(path):
    with Image.open(path) as im:return ''.join('1' if p>=128 else '0' for p in im.convert('L').resize((8,8)).getdata())
def audit(name,root):
    images=[p for p in root.rglob("*") if p.suffix.lower() in EXT];valid=[];corrupt=[];zero=[];digests={};exact=[];near=defaultdict(list);classes=Counter()
    for path in images:
        if path.stat().st_size==0:zero.append(str(path));continue
        try:
            with Image.open(path) as image:image.verify()
            digest=hashlib.sha256(path.read_bytes()).hexdigest()
            if digest in digests:exact.append({"path":str(path),"same_as":digests[digest]})
            else:digests[digest]=str(path);valid.append(path)
            near[ahash(path)].append(str(path));classes[path.parent.name]+=1
        except Exception:corrupt.append(str(path))
    near_groups=[v for v in near.values() if len(v)>1]
    report={"dataset":name,"root":str(root),"total_image_files":len(images),"valid_images":len(valid),"zero_byte_files":zero,"corrupt_images":corrupt,"unsupported_files":sum(1 for p in root.rglob("*") if p.is_file() and p.suffix.lower() not in EXT and p.name!="dataset_manifest.json"),"classes_by_parent_folder":dict(classes),"class_count_by_parent_folder":len(classes),"exact_duplicates":exact,"near_duplicate_hash_groups":near_groups,"imbalance_ratio":max(classes.values())/max(min(classes.values()),1) if classes else None}
    return report,digests,set(near)
def write(report,path):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2));path.with_suffix(".md").write_text(f"# {report['dataset']} audit\n\n- Images: {report['total_image_files']}\n- Valid: {report['valid_images']}\n- Classes by folder: {report['class_count_by_parent_folder']}\n- Corrupt: {len(report['corrupt_images'])}\n- Exact duplicates: {len(report['exact_duplicates'])}\n- Near-duplicate hash groups: {len(report['near_duplicate_hash_groups'])}\n")
def main():
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path("/data/raw/kaggle"));p.add_argument("--reports",type=Path,default=Path("/data/training/reports"));args=p.parse_args();results={}
    for name in ("indian_food_101","5000_indian_cuisines"):
        report,digests,near=audit(name,args.root/name);write(report,args.reports/f"{name}_audit.json");results[name]=(digests,near)
    left,right=results.values();cross={"exact_duplicate_count":len(set(left[0])&set(right[0])),"near_duplicate_hash_count":len(left[1]&right[1])};write({"dataset":"cross_dataset","total_image_files":0,"valid_images":0,"class_count_by_parent_folder":0,"corrupt_images":[],"exact_duplicates":[],"near_duplicate_hash_groups":[],**cross},args.reports/"cross_dataset_audit.json");print(json.dumps(cross,indent=2))
if __name__=="__main__":main()
