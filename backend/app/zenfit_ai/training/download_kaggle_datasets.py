"""Reproducible Kaggle acquisition. Credentials are never logged."""
import argparse,json,os,shutil
from datetime import datetime,timezone
from pathlib import Path

DATASETS={
 "indian_food_101":("nehaprabhavalkar/indian-food-101","indian_food_101"),
 "5000_indian_cuisines":("campusx/5000-indian-cuisines-datasetwith-images","5000_indian_cuisines"),
}

def manifest(dataset_id,destination,status,metadata=None):
    metadata=metadata or {}
    license_name=metadata.get("licenseName") or metadata.get("license") or "UNKNOWN"
    return {"dataset_name":metadata.get("title") or destination.name,"dataset_id":dataset_id,"dataset_version":str(metadata.get("versionNumber") or metadata.get("currentVersionNumber") or "unknown"),"source_platform":"Kaggle","source_url":f"https://www.kaggle.com/datasets/{dataset_id}","local_path":str(destination),"license":license_name,"license_source":"Kaggle dataset metadata","commercial_use_allowed":None,"redistribution_allowed":None,"research_use_allowed":None,"license_review_status":"pending","download_status":status,"downloaded_at":datetime.now(timezone.utc).isoformat() if status=="READY" else "","reviewed_by":"","reviewed_at":"","notes":"Permissions remain unknown until a human reviews the exact license terms."}

def download(key,root,force=False):
    dataset_id,folder=DATASETS[key];destination=root/folder;marker=destination/".download_incomplete"
    if destination.exists() and not marker.exists() and any(p.name!="dataset_manifest.json" for p in destination.iterdir()) and not force:return "READY",dataset_id
    if force and destination.exists():shutil.rmtree(destination)
    destination.mkdir(parents=True,exist_ok=True);marker.write_text("incomplete")
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api=KaggleApi();api.authenticate()
        metadata={}
        try:
            view=api.dataset_view(dataset_id);metadata=view.to_dict() if hasattr(view,"to_dict") else vars(view)
        except Exception:pass
        api.dataset_download_files(dataset_id,path=str(destination),unzip=True,quiet=False)
        files=[p for p in destination.rglob("*") if p.is_file() and p!=marker]
        if not files:raise RuntimeError("download produced no files")
        marker.unlink(missing_ok=True);(destination/"dataset_manifest.json").write_text(json.dumps(manifest(dataset_id,destination,"READY",metadata),indent=2));return "READY",dataset_id
    except Exception as exc:
        safe="KAGGLE AUTHENTICATION FAILED" if exc.__class__.__name__ in {"ApiException","ValueError"} or "auth" in str(exc).lower() or "401" in str(exc) or "403" in str(exc) else f"DOWNLOAD FAILED ({exc.__class__.__name__})"
        (destination/"dataset_manifest.json").write_text(json.dumps(manifest(dataset_id,destination,"FAILED"),indent=2));return safe,dataset_id

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--dataset",choices=DATASETS);parser.add_argument("--force",action="store_true");parser.add_argument("--root",type=Path,default=Path("/data/raw/kaggle"));args=parser.parse_args()
    if not os.getenv("KAGGLE_API_TOKEN"):raise SystemExit("KAGGLE AUTHENTICATION FAILED")
    print("Kaggle Dataset Acquisition")
    for key in ([args.dataset] if args.dataset else DATASETS):
        status,dataset_id=download(key,args.root,args.force);print(f"[{status}] {key}\nDataset ID: {dataset_id}")

if __name__=="__main__":main()
