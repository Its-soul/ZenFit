import argparse,json,math,statistics,time
from pathlib import Path
import numpy as np
from PIL import Image

def main():
    p=argparse.ArgumentParser();p.add_argument("version");p.add_argument("--models-dir",type=Path,default=Path("app/zenfit_ai/models/indian_food"));p.add_argument("--dataset",type=Path,default=Path("/data/training/indian_food_v2"));p.add_argument("--raw",type=Path,default=Path("/data/raw/kaggle/food_image_classification/Food Classification dataset"));args=p.parse_args();root=args.models_dir/args.version
    import torch
    from torch import nn
    from torch.utils.data import DataLoader
    from torchvision.datasets import ImageFolder
    from torchvision.models import efficientnet_b0,EfficientNet_B0_Weights
    classes=json.loads((root/"classes.json").read_text());cal=json.loads((root/"calibration.json").read_text());temperature=cal["temperature"];model=efficientnet_b0(num_classes=len(classes));model.load_state_dict(torch.load(root/"model.pt",map_location="cpu",weights_only=True));model.eval();transform=EfficientNet_B0_Weights.DEFAULT.transforms()
    val=ImageFolder(args.dataset/"val",transform);conf=[];correct=[]
    with torch.no_grad():
        for x,y in DataLoader(val,batch_size=32):probs=(model(x)/temperature).softmax(1);values,pred=probs.max(1);conf.extend(values.tolist());correct.extend((pred==y).tolist())
    def threshold(target):
        candidates=sorted(set(round(x,2) for x in conf))
        valid=[t for t in candidates if sum(c>=t for c in conf)>=max(20,int(len(conf)*.1)) and np.mean([ok for c,ok in zip(conf,correct) if c>=t])>=target]
        return min(valid) if valid else 1.0
    high=threshold(.95);medium=threshold(.85);unknown=min(.60,medium);thresholds={"high":high,"medium":medium,"low":unknown,"unknown_below":unknown,"minimum_margin":.10,"selected_on":"validation","note":"MVP confidence/margin rejection; not a dedicated food detector"};(root/"confidence_thresholds.json").write_text(json.dumps(thresholds,indent=2))
    def predict(image):
        start=time.perf_counter()
        with torch.no_grad():probs=(model(transform(image.convert('RGB')).unsqueeze(0))/temperature).softmax(1)[0]
        values,idx=probs.topk(2);confidence=float(values[0]);margin=float(values[0]-values[1]);entropy=float(-(probs*probs.clamp_min(1e-12).log()).sum());return {"label":classes[int(idx[0])],"confidence":confidence,"margin":margin,"entropy":entropy,"rejected":confidence<unknown or margin<thresholds["minimum_margin"],"latency_ms":(time.perf_counter()-start)*1000}
    unknown_results=[]
    for folder in ("burger","pizza","sushi","ice_cream","apple_pie"):
        for path in list((args.raw/folder).glob("*"))[:5]:
            try:unknown_results.append({"expected":"unknown_food","source_class":folder,**predict(Image.open(path))})
            except Exception:pass
    from sklearn.datasets import load_sample_image
    probes=[("china",Image.fromarray(load_sample_image("china.jpg"))),("flower",Image.fromarray(load_sample_image("flower.jpg"))),("blank",Image.new("RGB",(224,224),"white")),("noise",Image.fromarray(np.random.default_rng(42).integers(0,256,(224,224,3),dtype=np.uint8)))]
    nonfood=[{"probe":name,**predict(image)} for name,image in probes];latencies=[];sample=Image.open(next((args.raw/"idli").glob("*")))
    for _ in range(20):latencies.append(predict(sample)["latency_ms"])
    unknown_rate=np.mean([x["rejected"] for x in unknown_results]) if unknown_results else 0;nonfood_rate=np.mean([x["rejected"] for x in nonfood]);metrics=json.loads((root/"metrics.json").read_text());baseline=root.parent/"0.2.0"/"metrics.json";baseline_metrics=json.loads(baseline.read_text()) if baseline.exists() else None
    metrics["non_food_gate"]=bool(nonfood_rate>=.8 and len(nonfood)>=5);metrics["unknown_food_gate"]=bool(unknown_rate>=.8);metrics["latency_gate"]=bool(np.percentile(latencies,95)<1000);metrics["regression_gate"]=bool(not baseline_metrics or metrics["macro_f1"]>=baseline_metrics["macro_f1"]-.01);(root/"metrics.json").write_text(json.dumps(metrics,indent=2))
    evidence={"thresholds":thresholds,"validation_samples":len(val),"non_food":{"sample_count":len(nonfood),"rejection_rate":nonfood_rate,"gate":"PASS" if metrics["non_food_gate"] else "BLOCKED","results":nonfood},"unknown_food":{"sample_count":len(unknown_results),"rejection_rate":unknown_rate,"gate":"PASS" if metrics["unknown_food_gate"] else "BLOCKED","results":unknown_results},"latency":{"runs":len(latencies),"p50_ms":statistics.median(latencies),"p95_ms":float(np.percentile(latencies,95)),"gate":"PASS" if metrics["latency_gate"] else "BLOCKED"},"regression":{"baseline":"0.2.0","macro_f1_delta":metrics["macro_f1"]-baseline_metrics["macro_f1"],"gate":"PASS" if metrics["regression_gate"] else "BLOCKED"}};(root/"release_evidence.json").write_text(json.dumps(evidence,indent=2));print(json.dumps({k:v for k,v in evidence.items() if k not in ('non_food','unknown_food')}|{"non_food":{k:v for k,v in evidence['non_food'].items() if k!='results'},"unknown_food":{k:v for k,v in evidence['unknown_food'].items() if k!='results'}},indent=2))
if __name__=="__main__":main()
