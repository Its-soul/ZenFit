import argparse
import json
import platform
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def calibration(probs, truth, bins=10):
    import numpy as np

    confidence = probs.max(1)
    prediction = probs.argmax(1)
    edges = np.linspace(0, 1, bins + 1)
    reliability, ece = [], 0
    for low, high in zip(edges[:-1], edges[1:]):
        mask = (confidence > low) & (confidence <= high)
        count = int(mask.sum())
        accuracy = float((prediction[mask] == truth[mask]).mean()) if count else None
        mean = float(confidence[mask].mean()) if count else None
        if count:
            ece += count / len(truth) * abs(accuracy - mean)
        reliability.append({"lower": float(low), "upper": float(high), "count": count, "accuracy": accuracy, "confidence": mean})
    onehot = np.eye(probs.shape[1])[truth]
    return {"brier_score": float(((probs - onehot) ** 2).sum(1).mean()), "ece": float(ece), "reliability_bins": reliability}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("dataset", type=Path)
    p.add_argument("--models-dir", type=Path, default=Path("../data/models/indian_food"))
    p.add_argument("--config", type=Path, default=Path("training/configs/indian_food_v1.json"))
    p.add_argument("--version", required=True)
    p.add_argument("--dataset-version", required=True)
    p.add_argument("--epochs", type=int)
    p.add_argument("--batch-size", type=int)
    p.add_argument("--learning-rate", type=float)
    p.add_argument("--patience", type=int)
    p.add_argument("--num-workers", type=int)
    p.add_argument("--device", choices=("auto", "cuda", "cpu"), default="auto")
    p.add_argument("--require-cuda", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--smoke-samples-per-split", type=int, default=128)
    return p.parse_args()


def build_classifier_model(architecture: str, class_count: int, *, pretrained: bool):
    if architecture != "efficientnet_b0":
        raise ValueError(f"Unsupported classifier architecture: {architecture}")
    from torch import nn
    from torchvision.models import EfficientNet_B0_Weights, efficientnet_b0

    model = efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT if pretrained else None)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, class_count)
    return model


def build_evaluation_transform(config: dict):
    if config.get("architecture") != "efficientnet_b0":
        raise ValueError(f"Unsupported classifier architecture: {config.get('architecture')}")
    from torchvision.models import EfficientNet_B0_Weights

    return EfficientNet_B0_Weights.DEFAULT.transforms()


def main():
    args = parse_args()
    output = args.models_dir / args.version
    if output.exists():
        raise FileExistsError(f"Immutable model version already exists: {output}")
    cfg = json.loads(args.config.read_text())
    for key, value in {"batch_size": args.batch_size, "early_stopping_patience": args.patience, "num_workers": args.num_workers}.items():
        if value is not None:
            cfg[key] = value
    if args.epochs is not None:
        cfg["head_epochs"] = min(cfg.get("head_epochs", args.epochs), args.epochs)
        cfg["finetune_epochs"] = max(0, args.epochs - cfg["head_epochs"])
    if args.learning_rate is not None:
        cfg["head_learning_rate"] = cfg["finetune_learning_rate"] = args.learning_rate
    cfg["smoke_training_only"] = args.smoke
    if args.smoke:
        cfg.update({"epochs": 1, "head_epochs": 1, "finetune_epochs": 0})

    import numpy as np
    import torch
    from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, confusion_matrix, top_k_accuracy_score
    from torch import nn
    from torch.utils.data import DataLoader, Subset
    from torchvision import transforms
    from torchvision.datasets import ImageFolder
    from torchvision.models import EfficientNet_B0_Weights, efficientnet_b0

    seed = cfg["random_seed"]
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    device = torch.device("cuda" if args.device == "auto" and torch.cuda.is_available() else args.device if args.device != "auto" else "cpu")
    if args.require_cuda and device.type != "cuda":
        raise RuntimeError("CUDA is required for this run but is unavailable; stopped before training")
    if device.type == "cuda":
        torch.backends.cudnn.benchmark = True
        torch.cuda.reset_peak_memory_stats()

    aug = cfg.get("augmentation", {})
    normalize = transforms.Normalize([.485, .456, .406], [.229, .224, .225])
    train_transform = transforms.Compose([transforms.RandomResizedCrop(cfg["image_size"], scale=tuple(aug.get("random_resized_crop_scale", [.8, 1]))), transforms.RandomHorizontalFlip(aug.get("horizontal_flip_probability", .5)), transforms.RandomRotation(aug.get("rotation_degrees", 8)), transforms.ColorJitter(brightness=aug.get("brightness", .15), contrast=aug.get("contrast", .15), saturation=aug.get("saturation", .1)), transforms.ToTensor(), normalize])
    eval_transform = build_evaluation_transform(cfg)
    train = ImageFolder(args.dataset / "train", train_transform)
    val = ImageFolder(args.dataset / "val", eval_transform)
    test = ImageFolder(args.dataset / "test", eval_transform)
    if not train.classes or train.classes != val.classes or train.classes != test.classes:
        raise ValueError("Non-empty train/val/test class folders must match")

    counts = Counter(train.targets)
    weights = torch.tensor([len(train) / (len(train.classes) * counts[i]) for i in range(len(train.classes))], device=device)
    if args.smoke:
        rng = np.random.default_rng(seed)
        subset = lambda ds: Subset(ds, sorted(rng.choice(len(ds), min(len(ds), args.smoke_samples_per_split), replace=False).tolist()))
        train_run, val_run, test_run = subset(train), subset(val), subset(test)
    else:
        train_run, val_run, test_run = train, val, test
    workers = cfg.get("num_workers", 2)
    loader = lambda ds, shuffle=False: DataLoader(ds, batch_size=cfg["batch_size"], shuffle=shuffle, num_workers=workers, pin_memory=device.type == "cuda", persistent_workers=workers > 0)

    model = build_classifier_model(cfg["architecture"], len(train.classes), pretrained=True)
    model.to(device)
    loss_fn = nn.CrossEntropyLoss(weight=weights if cfg["weighted_loss"] else None)
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    output.mkdir(parents=True)
    best_loss, best_accuracy, best_epoch, wait, history, global_epoch = float("inf"), 0, 0, 0, [], 0
    for parameter in model.features.parameters():
        parameter.requires_grad = False
    stages = (("head", cfg.get("head_epochs", 3), cfg.get("head_learning_rate", 1e-3)), ("finetune", cfg.get("finetune_epochs", 5), cfg.get("finetune_learning_rate", 1e-4)))
    for stage, epochs, learning_rate in stages:
        if stage == "finetune":
            for block in list(model.features.children())[-cfg.get("unfreeze_last_blocks", 3):]:
                for parameter in block.parameters():
                    parameter.requires_grad = True
        optimizer = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad), lr=learning_rate)
        for _ in range(epochs):
            global_epoch += 1; model.train(); train_loss = train_correct = 0
            for x, y in loader(train_run, True):
                x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True); optimizer.zero_grad(set_to_none=True)
                with torch.amp.autocast("cuda", enabled=device.type == "cuda"):
                    logits = model(x); loss = loss_fn(logits, y)
                scaler.scale(loss).backward(); scaler.step(optimizer); scaler.update()
                train_loss += float(loss) * len(y); train_correct += int((logits.argmax(1) == y).sum())
            model.eval(); correct = total = 0; val_loss = 0
            with torch.no_grad():
                for x, y in loader(val_run):
                    x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
                    with torch.amp.autocast("cuda", enabled=device.type == "cuda"):
                        logits = model(x); batch_loss = loss_fn(logits, y)
                    val_loss += float(batch_loss) * len(y); correct += int((logits.argmax(1) == y).sum()); total += len(y)
            score = correct / max(total, 1); mean_val_loss = val_loss / max(len(val_run), 1)
            history.append({"epoch": global_epoch, "stage": stage, "learning_rate": learning_rate, "training_loss": train_loss / len(train_run), "training_accuracy": train_correct / len(train_run), "validation_loss": mean_val_loss, "validation_accuracy": score})
            if mean_val_loss < best_loss:
                best_loss, best_accuracy, best_epoch, wait = mean_val_loss, score, global_epoch, 0; torch.save(model.state_dict(), output / "model.pt")
            else:
                wait += 1
            if wait >= cfg["early_stopping_patience"]:
                break
        if wait >= cfg["early_stopping_patience"]:
            break

    model.load_state_dict(torch.load(output / "model.pt", map_location=device, weights_only=True)); model.eval()
    def infer(ds):
        logits, truth = [], []
        with torch.no_grad():
            for x, y in loader(ds):
                logits.append(model(x.to(device, non_blocking=True)).cpu()); truth.extend(y.tolist())
        return torch.cat(logits), np.asarray(truth)
    val_logits, val_truth = infer(val_run)
    temperature = torch.ones(1, requires_grad=True); optimizer = torch.optim.LBFGS([temperature], lr=.05, max_iter=50); ce = nn.CrossEntropyLoss()
    def closure():
        optimizer.zero_grad(); loss = ce(val_logits / temperature.clamp(.05, 10), torch.tensor(val_truth)); loss.backward(); return loss
    optimizer.step(closure); temp = float(temperature.detach().clamp(.05, 10))
    test_logits, truth = infer(test_run); probs = (test_logits / temp).softmax(1).numpy(); pred = probs.argmax(1)
    report = classification_report(truth, pred, labels=list(range(len(train.classes))), target_names=train.classes, output_dict=True, zero_division=0)
    matrix = confusion_matrix(truth, pred, labels=list(range(len(train.classes)))).tolist()
    metrics = {"sample_count": len(test_run), "accuracy": accuracy_score(truth, pred), "balanced_accuracy": balanced_accuracy_score(truth, pred), "macro_precision": report["macro avg"]["precision"], "macro_recall": report["macro avg"]["recall"], "macro_f1": report["macro avg"]["f1-score"], "weighted_precision": report["weighted avg"]["precision"], "weighted_recall": report["weighted avg"]["recall"], "weighted_f1": report["weighted avg"]["f1-score"], "top_3_accuracy": top_k_accuracy_score(truth, probs, k=min(3, len(train.classes)), labels=list(range(len(train.classes)))), "per_class": {name: report[name] for name in train.classes}, "history": history, "best_epoch": best_epoch, "best_validation_loss": best_loss, "best_validation_accuracy": best_accuracy, "checkpoint": "model.pt", "device": str(device), "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated() if device.type == "cuda" else None, "non_food_gate": False, "latency_gate": False, "regression_gate": False}
    cal = calibration(probs, truth) | {"temperature": temp, "fit_split": "validation", "evaluation_split": "test"}
    split_manifest = args.dataset / "split_manifest.json"
    dataset_manifest = json.loads(split_manifest.read_text()) if split_manifest.exists() else {"dataset_version": args.dataset_version, "sources": []}
    resolved = cfg | {"name": "indian_food_classifier", "version": args.version, "dataset_version": args.dataset_version, "class_count": len(train.classes), "training_images": len(train), "validation_images": len(val), "test_images": len(test), "created_at": datetime.now(timezone.utc).isoformat(), "status": "candidate", "device": str(device)}
    reproducibility = {"random_seed": seed, "python": platform.python_version(), "torch": torch.__version__, "torchvision": __import__("torchvision").__version__, "cuda": torch.version.cuda, "gpu": torch.cuda.get_device_name(0) if device.type == "cuda" else None, "command_config": resolved}
    weak = sorted(train.classes, key=lambda x: metrics["per_class"][x]["f1-score"])[:5]
    card = f"# Indian Food Classifier {args.version}\n\n- Architecture: EfficientNet-B0\n- Dataset version: {args.dataset_version}\n- Classes: {len(train.classes)}\n- Training/validation/test: {len(train)}/{len(val)}/{len(test)}\n- Macro F1: {metrics['macro_f1']:.4f}\n- ECE: {cal['ece']:.4f}\n- Weak classes: {', '.join(weak)}\n- Expected input: one food-focused RGB image\n- Unsupported: reliable multi-food localization, exact portions, unseen foods\n- Non-food/unknown behavior: conservative confidence/margin rejection; not a dedicated detector\n- Promotion: candidate; production requires all license and validation gates\n"
    for name, value in (("classes.json", train.classes), ("config.json", resolved), ("metrics.json", metrics), ("calibration.json", cal), ("dataset_manifest.json", dataset_manifest), ("confusion_matrix.json", matrix), ("reproducibility.json", reproducibility)):
        (output / name).write_text(json.dumps(value, indent=2))
    (output / "model_card.md").write_text(card)
    print(json.dumps({"version": args.version, "device": str(device), "metrics": metrics, "calibration": cal}, indent=2))


if __name__ == "__main__":
    main()
