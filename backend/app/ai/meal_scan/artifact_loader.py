from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile

from app.ai.artifacts import LocalArtifactStorage, storage_from_settings, verify_artifact


def selected_version(settings) -> str | None:
    if settings.meal_classifier_version:
        return settings.meal_classifier_version
    pointer_name = "active.json" if settings.meal_classifier_environment == "production" else "developer_beta.json"
    pointer = settings.artifact_local_dir / settings.meal_classifier_artifact_prefix / pointer_name
    if not pointer.is_file():
        pointer = settings.indian_food_model_path.parent / "indian_food" / pointer_name
    if not pointer.is_file():
        return None
    payload = json.loads(pointer.read_text(encoding="utf-8"))
    return payload.get("version")


def artifact_key(settings, version: str, filename: str = "") -> str:
    base = f"{settings.meal_classifier_artifact_prefix.strip('/')}/{version}"
    return f"{base}/{filename}" if filename else base


def _local_root(settings, version: str) -> Path:
    return settings.artifact_local_dir / artifact_key(settings, version)


def _cache_root(settings, version: str) -> Path:
    return settings.model_cache_dir / "artifacts" / artifact_key(settings, version)


def materialize_verified_artifact(settings) -> tuple[Path, dict]:
    if not settings.meal_classifier_enabled:
        raise RuntimeError("meal classifier disabled by configuration")
    version = selected_version(settings)
    if not version:
        raise FileNotFoundError("AI_MEAL_CLASSIFIER_VERSION is not configured and no developer-beta pointer exists")
    required_environment = settings.meal_classifier_environment
    storage = storage_from_settings(settings)
    if isinstance(storage, LocalArtifactStorage):
        root = _local_root(settings, version)
        manifest = verify_artifact(root, required_environment=required_environment)
        if manifest.get("model_version") != version:
            raise ValueError("artifact model version does not match selected version")
        return root, manifest

    root = _cache_root(settings, version)
    if root.is_dir():
        try:
            manifest = verify_artifact(root, required_environment=required_environment)
            if manifest.get("model_version") != version: raise ValueError("artifact model version does not match selected version")
            return root, manifest
        except ValueError:
            pass
    root.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{version}-", dir=root.parent))
    try:
        manifest_path = storage.fetch(artifact_key(settings, version, "artifact_manifest.json"), staging / "artifact_manifest.json")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for filename in manifest.get("files", {}):
            storage.fetch(artifact_key(settings, version, filename), staging / filename)
        verified = verify_artifact(staging, required_environment=required_environment)
        if verified.get("model_version") != version:
            raise ValueError("artifact model version does not match selected version")
        if root.exists():
            raise FileExistsError(f"Refusing to replace existing artifact cache: {root}")
        staging.rename(root)
        return root, verified
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def artifact_capability(settings) -> dict:
    version = selected_version(settings)
    base = {"enabled": settings.meal_classifier_enabled, "available": False, "model_version": version, "environment": settings.meal_classifier_environment}
    if not settings.meal_classifier_enabled:
        return base | {"reason": "classifier_disabled"}
    try:
        _, manifest = materialize_verified_artifact(settings)
        return base | {"available": True, "model_version": manifest.get("model_version", version), "reason": None}
    except Exception as exc:
        return base | {"reason": exc.__class__.__name__}
