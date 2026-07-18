from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shutil
from typing import Protocol

REQUIRED_FILES=("model.pt","classes.json","config.json","calibration.json","open_set_thresholds.json","metrics.json","dataset_manifest.json","model_card.md")


def sha256(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):digest.update(chunk)
    return digest.hexdigest()


class ArtifactStorage(Protocol):
    def put(self, source: Path, key: str) -> str: ...
    def fetch(self, key: str, destination: Path) -> Path: ...


@dataclass
class LocalArtifactStorage:
    root: Path

    def put(self, source: Path, key: str) -> str:
        destination=self.root/key;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,destination);return str(destination)

    def fetch(self, key: str, destination: Path) -> Path:
        destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(self.root/key,destination);return destination


class S3CompatibleArtifactStorage:
    def __init__(self,bucket:str,endpoint_url:str|None=None):self.bucket,self.endpoint_url=bucket,endpoint_url
    def _client(self):
        try:import boto3
        except ImportError as exc:raise RuntimeError("Install the optional boto3 dependency for S3-compatible storage") from exc
        return boto3.client("s3",endpoint_url=self.endpoint_url)
    def put(self,source:Path,key:str)->str:self._client().upload_file(str(source),self.bucket,key);return f"s3://{self.bucket}/{key}"
    def fetch(self,key:str,destination:Path)->Path:destination.parent.mkdir(parents=True,exist_ok=True);self._client().download_file(self.bucket,key,str(destination));return destination


def package_artifact(candidate: Path, destination: Path, *, environment: str) -> Path:
    if environment not in {"development","production"}:raise ValueError("environment must be development or production")
    if environment == "production":
        gate_path=candidate/"promotion_gates.json"
        if not gate_path.is_file():raise ValueError("production packaging requires promotion-gate evidence")
        gates=json.loads(gate_path.read_text(encoding="utf-8"))
        if not gates or any(item.get("status")!="PASS" for item in gates.values()):raise ValueError("production packaging blocked by promotion gates")
    missing=[name for name in REQUIRED_FILES if not (candidate/name).is_file()]
    if missing:raise ValueError("missing artifact files: "+", ".join(missing))
    destination.mkdir(parents=True,exist_ok=False)
    files={}
    for name in REQUIRED_FILES:
        target=destination/name;shutil.copy2(candidate/name,target);files[name]={"sha256":sha256(target),"size_bytes":target.stat().st_size}
    manifest={"schema_version":1,"model_version":candidate.name,"environment":environment,"files":files}
    (destination/"artifact_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    return destination


def verify_artifact(root: Path, *, required_environment: str|None=None) -> dict:
    manifest_path=root/"artifact_manifest.json"
    if not manifest_path.is_file():raise ValueError("artifact manifest missing")
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    if required_environment and manifest.get("environment")!=required_environment:raise ValueError("artifact environment mismatch")
    for name,metadata in manifest.get("files",{}).items():
        path=root/name
        if not path.is_file() or sha256(path)!=metadata.get("sha256"):raise ValueError(f"artifact checksum failed: {name}")
    missing=set(REQUIRED_FILES)-set(manifest.get("files",{}))
    if missing:raise ValueError("artifact manifest incomplete")
    return manifest


def storage_from_settings(settings):
    if settings.artifact_storage_backend=="local":return LocalArtifactStorage(settings.artifact_local_dir)
    if settings.artifact_storage_backend=="s3_compatible":
        if not settings.artifact_s3_bucket:raise ValueError("AI_ARTIFACT_S3_BUCKET is required")
        return S3CompatibleArtifactStorage(settings.artifact_s3_bucket,settings.artifact_s3_endpoint)
    raise ValueError("unsupported artifact storage backend")
