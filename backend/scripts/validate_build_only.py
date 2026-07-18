"""Static/configuration validator. It must never load an AI model."""
import ast
import os
from pathlib import Path

from app.ai.config import get_ai_settings
from app.ai.registry import ModelRegistry


def _calls_in(path: Path) -> set[str]:
    tree=ast.parse(path.read_text(encoding="utf-8"));calls=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Call):
            if isinstance(node.func,ast.Name):calls.add(node.func.id)
            elif isinstance(node.func,ast.Attribute):calls.add(node.func.attr)
    return calls


def validate() -> list[tuple[str,bool,str]]:
    settings=get_ai_settings();registry=ModelRegistry();app_root=Path(__file__).resolve().parents[1]/"app"
    main_calls=_calls_in(app_root/"main.py");worker_calls=_calls_in(app_root/"workers"/"main.py")
    storage_valid=settings.artifact_storage_backend in {"local","s3_compatible"} and (settings.artifact_storage_backend!="s3_compatible" or bool(settings.artifact_s3_bucket))
    disabled_registry=registry.prewarm()=={} and registry.get_food_classifier() is None and registry.get_embedding_model() is None and registry.get_reranker() is None
    return [
        ("Heavy AI models disabled",not settings.heavy_models_enabled,"AI_HEAVY_MODELS_ENABLED must be false"),
        ("AI prewarming disabled",settings.prewarm_models=="false","AI_PREWARM_MODELS must be false"),
        ("Classifier eager loading disabled",disabled_registry,"disabled registry must reject model loading"),
        ("BGE eager loading disabled",disabled_registry,"disabled registry must reject model loading"),
        ("Dataset auto-download disabled","download_kaggle_datasets" not in main_calls|worker_calls,"startup must not download datasets"),
        ("Training auto-run disabled",not ({"train_indian_food","fit"}&(main_calls|worker_calls)),"startup must not train"),
        ("Artifact storage configuration valid",storage_valid,"configure local or S3-compatible artifact storage"),
        ("Deployment configuration valid",os.getenv("AI_HEAVY_MODELS_ENABLED","false").lower() in {"false","0","no"},"deployment must begin with heavy models disabled"),
    ]


def main():
    print("ZenFit Build-Only Validation\n")
    results=validate()
    for label,passed,_ in results:print(f"[{'PASS' if passed else 'FAIL'}] {label}")
    if not all(passed for _,passed,_ in results):
        for label,passed,reason in results:
            if not passed:print(f"Reason ({label}): {reason}")
        raise SystemExit(1)
    print("\nNO AI MODELS WERE EXECUTED")


if __name__=="__main__":main()
