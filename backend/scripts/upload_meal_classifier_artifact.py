import argparse
from pathlib import Path

from app.ai.artifacts import storage_from_settings, verify_artifact
from app.ai.config import get_ai_settings
from app.ai.meal_scan.artifact_loader import artifact_key


def main():
    parser = argparse.ArgumentParser(description="Upload one verified meal-classifier artifact package")
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--environment", choices=("developer-beta", "production"), default="developer-beta")
    args = parser.parse_args()
    manifest = verify_artifact(args.artifact, required_environment=args.environment)
    if manifest.get("model_version") != args.version:
        raise SystemExit("Artifact manifest version does not match --version")
    settings = get_ai_settings(); storage = storage_from_settings(settings)
    filenames = list(manifest["files"])
    for filename in filenames:
        storage.put(args.artifact / filename, artifact_key(settings, args.version, filename))
    storage.put(args.artifact / "artifact_manifest.json", artifact_key(settings, args.version, "artifact_manifest.json"))
    print(f"Uploaded verified {args.environment} artifact {args.version} ({len(filenames) + 1} files)")


if __name__ == "__main__":
    main()
