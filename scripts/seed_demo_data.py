import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))


def parse_args():
    parser = argparse.ArgumentParser(description="Seed realistic demo history for AI Fitness OS.")
    parser.add_argument("--days", type=int, default=180, help="Number of historical days to generate.")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed.")
    parser.add_argument("--keep-existing", action="store_true", help="Do not delete existing demo users first.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    from app.core.qdrant_client import ensure_qdrant_collections
    from app.db.session import SessionLocal
    from app.demo.seeder import DemoDataSeeder

    ensure_qdrant_collections()
    db = SessionLocal()
    try:
        summaries = DemoDataSeeder(db, days=args.days, seed=args.seed, reset=not args.keep_existing).run()
        print("Seeded demo users:")
        for summary in summaries:
            skipped = " skipped existing" if summary.get("skipped") else ""
            print(f"- {summary['email']} / {summary['password']} ({summary['persona']}, {summary['days_seeded']} days){skipped}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
