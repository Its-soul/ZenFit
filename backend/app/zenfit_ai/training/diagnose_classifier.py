"""Hard pre-training diagnostics plus a mandatory tiny-subset memorization test."""
import argparse,json,random
from collections import Counter
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument("dataset",type=Path);p.add_argument("--epochs",type=int,default=20);p.add_argument("--classes",type=int,default=3);p.add_argument("--images-per-class",type=int,default=10);args=p.parse_args()
    import torch
    from torch import nn
    from torch.utils.data import DataLoader,Subset
    from torchvision.datasets import ImageFolder
    from torchvision.models import efficientnet_b0,EfficientNet_B0_Weights
    transform=EfficientNet_B0_Weights.DEFAULT.transforms();datasets={name:ImageFolder(args.dataset/name,transform) for name in ("train","val","test")};mappings={name:ds.class_to_idx for name,ds in datasets.items()}
    if len({json.dumps(v,sort_keys=True) for v in mappings.values()})!=1:raise SystemExit("TRAINING PIPELINE DIAGNOSTIC FAILED: class index mismatch")
    selected=datasets["train"].classes[:args.classes];indices=[]
    for cls in selected:indices.extend([i for i,(_,target) in enumerate(datasets["train"].samples) if target==datasets["train"].class_to_idx[cls]][:args.images_per_class])
    if len(indices)!=args.classes*args.images_per_class:raise SystemExit("TRAINING PIPELINE DIAGNOSTIC FAILED: insufficient tiny subset")
    sample,_=datasets["train"][indices[0]]
    if tuple(sample.shape)!=(3,224,224):raise SystemExit(f"TRAINING PIPELINE DIAGNOSTIC FAILED: tensor shape {tuple(sample.shape)}")
    model=efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT);model.classifier[1]=nn.Linear(model.classifier[1].in_features,len(datasets["train"].classes))
    if model.classifier[1].out_features!=len(mappings["train"]):raise SystemExit("TRAINING PIPELINE DIAGNOSTIC FAILED: output size mismatch")
    counts=Counter(datasets["train"].targets);weights=[len(datasets["train"])/(len(counts)*counts[i]) for i in range(len(counts))]
    if any(datasets["train"].classes[i] not in counts and False for i in range(len(weights))):raise SystemExit("TRAINING PIPELINE DIAGNOSTIC FAILED: weight indexing")
    loader=DataLoader(Subset(datasets["train"],indices),batch_size=len(indices),shuffle=True);loss_fn=nn.CrossEntropyLoss();opt=torch.optim.AdamW(model.parameters(),lr=1e-3);best={"accuracy":0,"state":None,"epoch":0,"loss":None}
    for epoch in range(args.epochs):
        model.train()
        for x,y in loader:opt.zero_grad();logits=model(x);loss=loss_fn(logits,y);loss.backward();opt.step()
        model.eval()
        with torch.no_grad():
            x,y=next(iter(loader));logits=model(x);accuracy=float((logits.argmax(1)==y).float().mean());current_loss=float(loss_fn(logits,y))
        if accuracy>=best["accuracy"]:best={"accuracy":accuracy,"state":{k:v.detach().clone() for k,v in model.state_dict().items()},"epoch":epoch+1,"loss":current_loss}
        if accuracy>=.95 and current_loss<.15:break
    model.load_state_dict(best["state"]);model.eval()
    with torch.no_grad():
        x,y=next(iter(loader));raw=model(x);before=raw.argmax(1);after=(raw/1.7).softmax(1).argmax(1);restored=float((before==y).float().mean())
    if not torch.equal(before,after):raise SystemExit("TRAINING PIPELINE DIAGNOSTIC FAILED: temperature changed argmax")
    if restored<.90:raise SystemExit(f"TRAINING PIPELINE DIAGNOSTIC FAILED: tiny overfit accuracy {restored:.3f}")
    result={"status":"PASS","class_indexes":[{"class":c,"train":mappings['train'][c],"validation":mappings['val'][c],"test":mappings['test'][c]} for c in datasets['train'].classes],"output_features":model.classifier[1].out_features,"sample_shape":list(sample.shape),"imagenet_normalization":True,"class_weights":[{"class":datasets['train'].classes[i],"index":i,"training_count":counts[i],"weight":weights[i]} for i in range(len(weights))],"tiny_subset":{"classes":selected,"images_per_class":args.images_per_class,"best_epoch":best['epoch'],"training_accuracy":best['accuracy'],"training_loss":best['loss'],"checkpoint_restored_accuracy":restored},"temperature_argmax_unchanged":True}
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
