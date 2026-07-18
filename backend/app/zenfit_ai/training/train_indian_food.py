import argparse,json,random,platform
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

def calibration(probs,truth,bins=10):
    import numpy as np
    confidence=probs.max(1);prediction=probs.argmax(1);edges=np.linspace(0,1,bins+1);reliability=[];ece=0
    for low,high in zip(edges[:-1],edges[1:]):
        mask=(confidence>low)&(confidence<=high);count=int(mask.sum());accuracy=float((prediction[mask]==truth[mask]).mean()) if count else None;mean=float(confidence[mask].mean()) if count else None
        if count:ece+=count/len(truth)*abs(accuracy-mean)
        reliability.append({"lower":float(low),"upper":float(high),"count":count,"accuracy":accuracy,"confidence":mean})
    onehot=np.eye(probs.shape[1])[truth];return {"brier_score":float(((probs-onehot)**2).sum(1).mean()),"ece":float(ece),"reliability_bins":reliability}

def main():
    p=argparse.ArgumentParser();p.add_argument("dataset",type=Path);p.add_argument("--models-dir",type=Path,default=Path("app/zenfit_ai/models/indian_food"));p.add_argument("--config",type=Path,default=Path("app/zenfit_ai/training/configs/indian_food_v1.json"));p.add_argument("--version",required=True);p.add_argument("--dataset-version",required=True);p.add_argument("--epochs",type=int);p.add_argument("--batch-size",type=int);p.add_argument("--learning-rate",type=float);p.add_argument("--patience",type=int);p.add_argument("--smoke",action="store_true");args=p.parse_args();output=args.models_dir/args.version
    if output.exists():raise FileExistsError(f"Immutable model version already exists: {output}")
    cfg=json.loads(args.config.read_text());cfg.update({k:v for k,v in {"epochs":args.epochs,"batch_size":args.batch_size,"learning_rate":args.learning_rate,"early_stopping_patience":args.patience}.items() if v is not None});cfg["smoke_training_only"]=args.smoke
    if args.smoke:cfg["epochs"]=min(cfg["epochs"],2)
    import numpy as np,torch
    from sklearn.metrics import accuracy_score,balanced_accuracy_score,classification_report,confusion_matrix,top_k_accuracy_score
    from torch import nn
    from torch.utils.data import DataLoader
    from torchvision.datasets import ImageFolder
    from torchvision.models import efficientnet_b0,EfficientNet_B0_Weights
    seed=cfg["random_seed"];random.seed(seed);np.random.seed(seed);torch.manual_seed(seed);transform=EfficientNet_B0_Weights.DEFAULT.transforms();train=ImageFolder(args.dataset/"train",transform);val=ImageFolder(args.dataset/"val",transform);test=ImageFolder(args.dataset/"test",transform)
    if not train.classes or train.classes!=val.classes or train.classes!=test.classes:raise ValueError("Non-empty train/val/test class folders must match")
    counts=Counter(train.targets);weights=torch.tensor([len(train)/(len(train.classes)*counts[i]) for i in range(len(train.classes))]);load=lambda ds,shuffle=False:DataLoader(ds,batch_size=cfg["batch_size"],shuffle=shuffle,num_workers=0)
    model=efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT);model.classifier[1]=nn.Linear(model.classifier[1].in_features,len(train.classes));loss_fn=nn.CrossEntropyLoss(weight=weights if cfg["weighted_loss"] else None);opt=torch.optim.AdamW(model.parameters(),lr=cfg["learning_rate"]);output.mkdir(parents=True)
    best=-1;wait=0;history=[]
    for epoch in range(cfg["epochs"]):
        model.train();train_loss=0
        for x,y in load(train,True):opt.zero_grad();loss=loss_fn(model(x),y);loss.backward();opt.step();train_loss+=float(loss)*len(y)
        model.eval();correct=total=0;val_loss=0
        with torch.no_grad():
            for x,y in load(val):logits=model(x);val_loss+=float(loss_fn(logits,y))*len(y);correct+=int((logits.argmax(1)==y).sum());total+=len(y)
        score=correct/max(total,1);history.append({"epoch":epoch+1,"training_loss":train_loss/len(train),"validation_loss":val_loss/max(len(val),1),"validation_accuracy":score})
        if score>best:best=score;wait=0;torch.save(model.state_dict(),output/"model.pt")
        else:wait+=1
        if wait>=cfg["early_stopping_patience"]:break
    model.load_state_dict(torch.load(output/"model.pt",map_location="cpu",weights_only=True));model.eval()
    def infer(ds):
        logits=[];truth=[]
        with torch.no_grad():
            for x,y in load(ds):logits.append(model(x));truth.extend(y.tolist())
        logits=torch.cat(logits);return logits,np.asarray(truth)
    val_logits,val_truth=infer(val);temperature=torch.ones(1,requires_grad=True);optimizer=torch.optim.LBFGS([temperature],lr=.05,max_iter=50);ce=nn.CrossEntropyLoss()
    def closure():optimizer.zero_grad();loss=ce(val_logits/temperature.clamp(.05,10),torch.tensor(val_truth));loss.backward();return loss
    optimizer.step(closure);temp=float(temperature.detach().clamp(.05,10));test_logits,truth=infer(test);probs=(test_logits/temp).softmax(1).numpy();pred=probs.argmax(1);report=classification_report(truth,pred,target_names=train.classes,output_dict=True,zero_division=0);matrix=confusion_matrix(truth,pred).tolist()
    metrics={"sample_count":len(test),"accuracy":accuracy_score(truth,pred),"balanced_accuracy":balanced_accuracy_score(truth,pred),"macro_precision":report["macro avg"]["precision"],"macro_recall":report["macro avg"]["recall"],"macro_f1":report["macro avg"]["f1-score"],"weighted_precision":report["weighted avg"]["precision"],"weighted_recall":report["weighted avg"]["recall"],"weighted_f1":report["weighted avg"]["f1-score"],"top_3_accuracy":top_k_accuracy_score(truth,probs,k=min(3,len(train.classes)),labels=list(range(len(train.classes)))),"per_class":{name:report[name] for name in train.classes},"history":history,"best_validation_accuracy":best,"non_food_gate":False,"latency_gate":False,"regression_gate":False}
    cal=calibration(probs,truth)|{"temperature":temp,"fit_split":"validation","evaluation_split":"test"};split_manifest=args.dataset/"split_manifest.json";dataset_manifest=json.loads(split_manifest.read_text()) if split_manifest.exists() else {"dataset_version":args.dataset_version,"sources":[]}
    resolved=cfg|{"name":"indian_food_classifier","version":args.version,"dataset_version":args.dataset_version,"class_count":len(train.classes),"training_images":len(train),"validation_images":len(val),"test_images":len(test),"created_at":datetime.now(timezone.utc).isoformat(),"status":"candidate"}
    reproducibility={"random_seed":seed,"python":platform.python_version(),"torch":torch.__version__,"torchvision":__import__("torchvision").__version__,"command_config":resolved}
    weak=sorted(train.classes,key=lambda x:metrics["per_class"][x]["f1-score"])[:5]
    card=f"# Indian Food Classifier {args.version}\n\n- Architecture: EfficientNet-B0\n- Dataset version: {args.dataset_version}\n- Classes: {len(train.classes)}\n- Training/validation/test: {len(train)}/{len(val)}/{len(test)}\n- Macro F1: {metrics['macro_f1']:.4f}\n- ECE: {cal['ece']:.4f}\n- Weak classes: {', '.join(weak)}\n- Expected input: one food-focused RGB image\n- Unsupported: reliable multi-food localization, exact portions, unseen foods\n- Non-food/unknown behavior: conservative confidence/margin rejection; not a dedicated detector\n- Promotion: candidate; production requires all license and validation gates\n"
    for name,value in (("classes.json",train.classes),("config.json",resolved),("metrics.json",metrics),("calibration.json",cal),("dataset_manifest.json",dataset_manifest),("confusion_matrix.json",matrix),("reproducibility.json",reproducibility)):(output/name).write_text(json.dumps(value,indent=2))
    (output/"model_card.md").write_text(card);print(json.dumps({"version":args.version,"metrics":metrics,"calibration":cal},indent=2))
if __name__=="__main__":main()
