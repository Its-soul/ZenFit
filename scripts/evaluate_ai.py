import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.ai.evaluation.runner import run_all_evaluations


if __name__ == "__main__":
    results = run_all_evaluations()
    print(results)
    if results["passed"] != results["total"]:
        raise SystemExit(1)
